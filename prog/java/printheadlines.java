// Datei: prog/java/printheadlines.java
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

import java.io.IOException;

public class printheadlines {

  private static String url = "https://heise.de/newsticker/";
  void main(String[] args) throws IOException {
    IO.println("Fetching "+ url);

    Document doc = Jsoup.connect(url).get();
    Elements news = doc.select("article.a-article-teaser");

    IO.println("\nNews: "+ news.size());
    for (Element item : news) {
      IO.println("* "+ item.text());
    }
  }
}

