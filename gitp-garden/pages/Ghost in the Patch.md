public:: true

- This is a Synth Animism acolytes' log. The [[Ghostpatch Guild]] tinker with [[Etherial Receivers]] like the [[Microfreak]], tuning into the signals of the [[Sound Spirits]] of the Misty Soundwood. Ghosts are in the garden, growing things, so be aware.
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