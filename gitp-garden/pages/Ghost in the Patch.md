public:: true

- Acolytes of the [[Ghostpatch Guild]], tinkering with [[Etherial Receivers]] such as the [[Microfreak]], tuning into the signals of the [[Sound Spirits]] of the Misty Soundwood. Ghosts in the garden, growing signal *awareness*.
- Subscribe to the podcast RSS feed at https://codekiln.github.io/gitpa/rss.xml
- ![gitp_logo_raw_fly.JPG](../assets/gitp/logo/gitp_logo_raw_fly.JPG){:height 778, :width 770}
- query-table:: false
  query-properties:: [:page]
  #+BEGIN_QUERY
  {:title [:h2 "Recent Ceremonies"]
   :query [:find (pull ?b [*])
           :where
           [?b :block/name]
           [?b :block/properties ?props]
           [(get ?props :logseq-entity) ?entities]
           [(contains? ?entities "Logseq/Entity/Podcast/Episode")]
           [(get ?props :public) ?public]
           [(= ?public true)]]
   :result-transform (fn [rows] (sort-by (fn [row] (get-in row [:block/properties :podcast-published-at])) (fn [a b] (compare b a)) rows))
   :view (fn [rows]
           [:ul (for [row rows]
                  [:li [:a {:href (str "#/page/" (clojure.string/replace (:block/name row) "/" "%2F"))}
                         (:block/original-name row)]])])
   :table-view? false
  }
  #+END_QUERY
