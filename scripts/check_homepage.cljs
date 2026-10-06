(ns check-homepage
  (:require ["fs" :as fs]
            ["os" :as os]
            ["path" :as path]
            ["child_process" :as child]
            [clojure.string :as str]
            [clojure.walk :as walk]
            [cljs.reader :as reader]
            [datascript.core :as d]
            [logseq.graph-parser.cli :as parser]))

(def source (or (first *command-line-args*) "gitp-garden"))
(def temporary (.mkdtempSync fs (path/join (.tmpdir os) "gitpa-query-")))
(def graph (path/join temporary "prepared"))
(.execFileSync child "python3" #js ["scripts/prepare_site.py" "--source" source "--output" graph])
(def content (.readFileSync fs (str graph "/pages/Ghost in the Patch.md") "utf8"))
(def query-text (second (re-find #"(?s)#\+BEGIN_QUERY\s*(.*?)\s*#\+END_QUERY" content)))
(def query-map (reader/read-string query-text))
(def transform (eval (:result-transform query-map)))
(def view (eval (:view query-map)))
(def conn (:conn (parser/parse-graph graph {:verbose false})))
;; Logseq rewrites (pull ?b [*]) to a fixed block attribute list before running
;; an advanced query, so ?b results lose :block/name and :block/original-name.
;; Source: frontend.db.query-custom/replace-star-with-block-attrs! and
;; frontend.db.model/block-attrs at logseq 0.10.6, the publish-spa default.
(def logseq-block-attrs
  '[:db/id :block/uuid :block/parent :block/left :block/collapsed? :block/format
    :block/refs :block/_refs :block/path-refs :block/tags :block/content :block/marker
    :block/priority :block/properties :block/properties-order :block/properties-text-values
    :block/pre-block? :block/scheduled :block/deadline :block/repeated? :block/created-at
    :block/updated-at :block/heading-level :block/file
    {:block/page [:db/id :block/name :block/original-name :block/journal-day]}])
(defn logseq-query [query]
  (walk/postwalk
    (fn [form]
      (if (and (seq? form) (= 'pull (first form)) (= '?b (second form)) (= '[*] (nth form 2 nil)))
        (list 'pull '?b logseq-block-attrs)
        form))
    query))
(defn result [db]
  (transform (map first (d/q (logseq-query (:query query-map)) db))))
(def expected
  (->> (d/q '[:find (pull ?p [*]) :where [?p :block/name]] @conn)
       (map first)
       (filter #(and (= true (get-in % [:block/properties :public]))
                     (contains? (get-in % [:block/properties :logseq-entity] #{}) "Logseq/Entity/Podcast/Episode")))
       (sort-by #(js/Date.parse (get-in % [:block/properties :podcast-published-at])) >)
       (map :block/name)))
(def actual (map :block/name (result @conn)))
(def rendered-view (view (result @conn)))
(def links (for [li (rest rendered-view)] (second li)))
(assert (= (count expected) (count links)) "Homepage view must link every episode")
(assert (every? #(and (= "a" (first %)) (str/starts-with? (get-in % [1 :href]) "#/page/")
                     (not (str/blank? (nth % 2)))) links) "Homepage episode link or label missing")
(assert (seq expected) "No public episodes parsed")
(assert (= expected actual) (str "Homepage differs: " actual " expected " expected))
(def drafts ["false" "true" false])
(def draft-db
  (d/db-with @conn
    (map-indexed
      (fn [i public] {:db/id (- -1 i) :block/name (str "draft-" i)
                     :block/properties {:public public :logseq-entity #{"Logseq/Entity/Podcast/Episode"}
                                        :podcast-published-at "2099-01-01"}})
      drafts)))
(assert (= actual (map :block/name (result draft-db))) "Draft or string public value leaked into homepage")
(println "Homepage query returns published episodes newest first:" (str/join ", " actual))

;; A real parsed fixture catches timezone ordering independently of the transform.
(def fixture-source (path/join temporary "fixture"))
(.cpSync fs source fixture-source #js {:recursive true})
(doseq [[name date public] [["timezone-earlier" "2099-10-05T10:00:00+02:00" "true"]
                           ["timezone-later" "2099-10-05T09:00:00Z" "true"]
                           ["unpublished" "2100-01-01T00:00:00Z" "false"]]]
  (.writeFileSync fs (path/join fixture-source "pages" (str name ".md"))
    (str "public:: " public "\nlogseq-entity:: [[Logseq/Entity/Podcast/Episode]]\npodcast-published-at:: " date "\n- # Fixture\n")))
(def fixture (path/join temporary "fixture-prepared"))
(.execFileSync child "python3" #js ["scripts/prepare_site.py" "--source" fixture-source "--output" fixture])
(def fixture-conn (:conn (parser/parse-graph fixture {:verbose false})))
(def fixture-names (map :block/name (result @fixture-conn)))
(assert (= ["timezone-later" "timezone-earlier"] (vec (take 2 fixture-names))) "Timezone ordering is wrong")
(assert (not (some #{"unpublished"} fixture-names)) "Parsed draft leaked into query")
(.rmSync fs temporary #js {:recursive true :force true})
(println "Timezone and unpublished fixtures pass")
