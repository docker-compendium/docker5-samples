// Datei: prog/nodejs/printheadlines.js

const Parser = require('rss-parser')
  parser = new Parser();

parser.parseURL('https://www.heise.de/newsticker/heise-atom.xml')
  .then(feed => {
    feed.items.forEach(entry => {
      console.log("* [%s]: %s",
        new Date(entry.pubDate).toISOString().replace('T', ' ').slice(0, 19),
        entry.title);
    })
  });

