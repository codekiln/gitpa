public:: true

- Acolytes of the [[Ghostpatch Guild]], tinkering with [[Etherial Receivers]] such as the [[Microfreak]], tuning into the signals of the [[Sound Spirits]] of the Misty Soundwood. Ghosts in the garden, growing signal *awareness*.
- ![gitp_logo_raw_fly.JPG](../assets/gitp/logo/gitp_logo_raw_fly.JPG){:height 778, :width 770}
- query-table:: false
  query-properties:: [:page]
  query-sort-by:: page
  query-sort-desc:: false
  #+BEGIN_QUERY
  {:title [:h2 "Recent Ceremonies"]
   :query [:find (pull ?b [*])
           :where
           (property ?b :type "Podcast/Episode")]
  :table-view? true
  }
  #+END_QUERY