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

Die Höhe als em festzulegen ist keine gute Idee. Schon deshalb, weil man nie genau weiß wie groß es tatsächlich wird und ob es mit anderen Inhalten in der Breite kollidiert. M ein Vorschlag wäre, das Logo in eine Column des Grid Systems (siehe nächster Punkt) zu setzen, und auf width=100%. Dann passt es sich in den zur Verfügung stehenden Platz ein. Falls das System auf Fluid gesetzt ist und potentiell ewig breit werden kann, dann kann man das Bild noch mit max-width=500px (z.B.) begrenzen.



### 2c) (Grid-) Layout

Das mit dem `container` vs `container-fluid` ist hier erklärt: http://getbootstrap.com/css/#grid . Hier kürzer in eigenen Worten: 

Inhalte, die nebeneinander dargestellt werden sollen, werden immer innerhalb eines `.container` (feste Breite) oder `.container-fluid` (100% des Bildschirms platziert). 

Wenn der Container fluid ist, dann ist er immer 100% des Bildschirms. Wenn er nicht fluid ist, ist er bei beliebig großen Bildschirmen immer 1200 Pixel breit (egal ob de Bildschirm 1300 oder 2800 Pixel hat). Wenn der Bildschirm kleiner als 1200 Pixel ist, ist der .container immer 960 Pixel breit (egal ob der Bildschirm 1000 oder 1199 Pixel breit ist). Das geht dann stufenweise herunter bis hin zu kleinen Bildschirmen. Aber es gibt immer den "breakpoint", bei dem der Container dann eine Stufe kleiner wird. 

Innerhalb eines containers können "columns" gepackt werden. Es ist immer Platz für 12 columns. Ich kann also 12 x `<div class="col-1"></div>` unterbringen, oder 2 x `<div class="col-6"></div>` oder `<div class="col-8"></div><div class="col-2"></div><div class="col-2"></div>` usw. Und diese Columns sind immer gleich breit. Je nach Bildschirmgröße und Größe des Containers passen sich dann die Columns an.

    <div class="container-fluid col-md-8 col-md-offset-2">

Müsste, korrekt angewendet, so hier aussehen: 

    <div class="container-fluid">
        <div class="row">
            <div class="col-md-8 col-md-offset-2"> ... content ... </div>
        </div>
    </div>

Das würde dann sagen: alles was bei "... content ..." steht, hat 66,6% der Bildschirmbreite (col-md-8). Und hat nach links einen Abstand von 16% (col-md-offset-2). Beides gilt aber nur ab einer Bildschirmbreite von 992 Pixeln (dafür sorgt das "md" Segment). Mit dem Kürzel xs, sm, md und lg kann man genauer unterscheiden, für welche Geräte die Spalten-Aufteilung gelten soll (bei kleinen Geräten mit 400 Pixeln Breite machen 12 Spalten wenig Sinn, da will man vielleicht eher umbrechen und die untereinander darstellen). Bei col-md-4 (usw) werden die Spalten bei Bildchirmen größer als 992 Pixel aufrecht erhalten. Wird der Bildschirm kleiner, werden alle md Spalten untereinander dargestellt anstatt nebeneinander. sm Spalten sind ab 768 Pixeln nebenaindner, darunter brechen sie um und werden untereinander dargestellt. xs Spalten sind immer nebeneinander. 

Mit dem Wissen kann man sich dann überlegen: wie sollen unsere Seiten dargestellt werden? Immer volle Bildschirmbreite (container-fluid), oder feste Breite mit maximal 1200 Pixeln (container)? Ich plädiere für die feste Breite, weil man sonst bei sehr großen Bildschirmen auch sehr breite Textzeilen bekommt, und diese nicht mehr lesen kann. Und dann: wie breit sollen die Inhalte sein? Und muss die Breite überhaupt angegeben werden? In der Nav-Bar z.B. ist sowieso das Logo links und die Punkte rechts, da kann die Breite egal sein. (Erst wenn die Inhalte ineinander ragen, müsste man sich etwas überlegen.) Bei article.html wollen wir ja links den Artikel und rechts das Sharing haben .. hier kann man dann Grid mit 8-4 oder 10-2 verwenden. 

Es gibt auch WYSIWYG-Editoren fürs Bootstrap Grid: http://shoelace.io/ , http://www.layoutit.com/build . Was die taugen, weiß ich nicht.

Ich baue an den Seiten jetzt nichts um. 


### 2d) Article List Page (article-list-page.html)

Erste Sache die wich wichtig finde: solche Mockups immer mit echten Inhalten machen! Das Wort "Artikel" wirkt und funktioniert natürlich ganz anders als wenn dort steht "Manchester United defender Ferdinand retires from international football". Damit wäre dann aufgefallen, dass die "table-responsive" Klasse ganz komische Sachen macht bei längeren Texten. Und auch sonst fallen bei dem richtigen HTML Mockup Dinge auf, die man im Wireframe nicht sofort sieht: 

- Fie diff-list-page.html funktioniert mit richtigen Überschriften ganz anders. Im Moment ist "Schlagzeile" die schmalste Spalte, und die anderen heben viel Platz. Wenn richtige Überschriften drin ständen, sähe die ganze Tabelle anders aus. (Und in der letzten Spalte würden die "Vergleichen mit vorheriger Version" umbrechen, wenn `.btn` nicht die Eigenschaft `white-space: nowrap;` hätte.)
- Ich würde Zeitung/Quelle nicht mehr in eine seperate Spalte nehmen. Vor Allem weil das auf verschiedenen Bildschirmen und mit verscheidenen Ǘberschrift-Längen immer komische Effekte gibt. Die Zeitung einfach in Klammern hinter den Titel schreiben wie bei newsdiffs.org scheint sinnvoll. 
- Alternative: "Original-Artikel bei ZEIT.de lesen" als kleine Zeile unter den Titel ... oder den Link zum Original erst auf der Detailseite bringen. Die Leute sollen ja nicht gleich auf unserer Liste 100 Links nach draußen finden.


Ich würde die ganze Auflistung nochmal zur Diskussion stellen, und anhand unserer funktionierenden Seite weiterentwickeln. Und daher am bisherigen Code nichts optimieren. 

Aber ein paar Hinweise zum Code möchte ich noch geben: 

- Warum die ganzen <ul> und <li>? Die machen hier keinen Sinn. Innerhalb einer Zeile sidn Titel, Änderungen, Datum, Vergleichen und Verlauf keine Auflistung.
- "Vergleichen" und "Artikelverlauf" sind semantisch keine Buttons sondern Links. Statt `<button type="button" class="btn btn-default">` geht auch `<a class="btn btn-default">`, was dasselbe Styling hat aber eben ein Link ist.
- In den Buttons wie im Footer habt ihr die Icons als Bilder eingebunden. Besser ist es, die als CSS_Eigenschaft zu verwenden. Denn sie sind kein Inhalt, sondern ein Gestaltungsmerkmal. Wie das geht würde ich aber später mal erklären. Für den Moment funktioniert das gut so.

Again: Keine Kritik sondern Hinweise.