## (1) Handwerkliches

- fehlendes/falsch verlinktes Bild zu GitHub sieht man schona uf der Seite, und auch in der Chrome Developer Toolbar. Da war nur der Dateiname falsch geschrieben - easy fix. Beim Entwickeln hab ich meistens die DevToolbar offen, dann sieht man solche Sachen sofort (weil Fehlermeldungen auftauchen). 
- <html> Tag am Ende der Seite nicht geschlossen, sondern nochmal geöffnet.
- HTML Syntax sollte man immer checken. Sonst können Fehler auftreten, bei denen man verzweifelt im CSS sucht, dabei ist das Problem im HTML. Manche IDe warnen bei ungültigem HTML. Oder man nimmt einen Validator (https://validator.w3.org/check)
- Klasse doppelt vergeben (`class="btn btn-default btn-default"`). Ist kein Problem, und passiert halt. Wollte nur kurz drauf hinweisen.
- JavaScript Dateien sollte man nicht im `<head>` einbinden, sondern als letztes im `<head>`. Das macht die Seite schneller. Wenn das JS im Head ist, unterbricht der Browser das Rendern der Seite bis er die JS Datei heruntergeladen und ausgewertet hat, und macht danach erst mit der Darstellung der Seite weiter. Wenn man das JS in den Fußm der Seite verbannt, kann schonmal alles dargestelt werden bevor das JS geladen wird.

Commit: **[Frontend/Static-HTML-Templates-Fixes 9aa7eec] fixed HTML syntax errors**


## (2) Layout 

Da hilft es grundsätzlich nur, sich die Elemente in der Developer Toolbar anzuschauen und mit den Klassen und ihren Eigenschaften zu testen / zu arbeiten.

Die Eigenschaften zu verstehen, ist natürlich schwer wenn man noch keine Frontend Erfahrung hat. Da hilft nur lernen und üben - wie bei Allem.

### 2b) Navi, Footer und #content 

    #content {
        min-height: 100%;
        height: auto !important;
        height: 100%;
        /* Negative indent footer by its height */
        margin: 0 auto -3em;
        /* Pad bottom by footer height */
        padding: 0 0 3em;
    }

Hier überschreiben Regeln sich zum Teil selbst (height 100% und dann wieder auf auto gesetzt via important). Ich vermute, das war gedacht um den Footer auf der Startseite an den unteren Bildchirmrand zu zwingen, wenn zu wenig Inhalt da ist. Dafür gibt es bei Bootstrap schon eine Lösung: http://getbootstrap.com/examples/sticky-footer-navbar/ (gefunden bei http://getbootstrap.com/getting-started/ , wo es eine Liste von Layout-Best-Practices gibt).

Von dort habe ich das Layout mal übernommen (navbar, content, footer).

In den statischen Entwürfen war auch die Navbar innerhalb des Content untergebracht, was syntaktisch nicht korrekt ist. 

    <body>
        <div id="content">
            <nav></nav>
            <div class="container">
        </div>
        <footer class="footer"></footer>
    </body>

Besser: Navbar, Content und Footer auf gleicher Hierarchie direkt im Body.

    <body>
        <nav></nav>
        <div id="content" class="container"></div>
        <footer class="footer"></footer>
    </body>

So macht es auch das Bootstrap-Beispiel das ich oben verlinkt habe.

Commit: **[Frontend/Static-HTML-Templates-Fixes 2b5f428] layout with nav, content, sticky footer**


### 2b) Navbar Styling

Auch hier: sowas passiert. Vor Allem weil ihr ja am Anfang mehr damit beschäftigt seid dass es überhaupt funktioniert als dass die beste Methode für den blöden Rahmen gewählt wird. Deswegen: nehmt das einfach mit als Hinweis.

**Border**

    .navbar-default {
        height: 6em;
        border-radius: 0;
        border-color: #FFFFFF;
        background-color: #FFFFFF;
    }

Den Border sollte man direkt ausblenden, anstatt die Farbe auf die Hintergrundfarbe zu setzen. Das spart auch den Radius (der in beiden Fällen, bei gleicher Farbe oder beim Ausblenden, nicht zu sehen ist):

    .navbar-default {
        height: 6em;
        border: none;
        background-color: #FFFFFF;
    }

**Logo Image**

Die Höhe als em festzulegen ist keine gute Idee. Scon deshalb, weil man nie genau weiß wie groß es tatsächlich wird und ob es mit anderen inhalten in der Breite kollidiert. 




### 2c) (Grid-) Layout

Das mit dem `container` vs `container-fluid` ist hier erklärt: http://getbootstrap.com/css/#grid . Hier kürzer in eigenen Worten: 


.....