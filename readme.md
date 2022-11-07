# Masterarbeit: Konzeption und Entwicklung eines Chatbots zur Unterstützung von Studierenden bei Selbstlernaktivitäten

***

## Table of Contents
1. Allgemeine Informationen
2. Laden und sprechen mit dem entwickleten Chatbot TED
3. Installation von Rasa Open Source
4. Beschreibung der Inhalte der einzelnen Dateien
5. Integration auf einer Website



## 1. Allgemeine Informationen
***
Dieser Chatbot wurde im Rahmen der Masterarbeit "Konzeption und Entwicklung eines Chatbots zur Unterstützung von Studierenden bei Selbstlernaktivitäten" von Julian Brändle entwickelt.
Dabei soll der Chatbot zwei wesentliche Aufgaben erfüllen:
1) Beantwortung allgemeiner Fragen zum Projekt
2) Suche nach Selbstlernmaterialien 

Entwickelt wurde der Chatbot mit RASA Open Source (2.8.14), Rasa Action Server (2.8.6)
(aktuellste Version: 3.x)
--> Die Verwendung von Rasa 3.x kann zur einer eingeschränkten Funktionsweise des Projekts führen.



## 2. Laden und sprechen mit dem entwickleten Chatbot TED:
***
Achtung:    Bevor der Chatbot (das trainierte Modell) geladen und mit dem Chatbot interagiert werden kann,
            ist es notwendig den Rasa Action Server zu starten (Lokal).

            Eingabe in der Komandozeile:

            1) Starten des Actions Server, der Rasa SDK verwendet
                rasa run actions

            2) Laden des Chatbots:
                rasa shell          (Lädt das trainiertes Modell und ermöglicht es, mit Ihrem Assistenten über die Befehlszeile zu sprechen.)
                rasa x              (Startet Rasa X im lokalen Modus)




## 3. Installation von Rasa Open Source
****
Alle Informationen zur Installation von RASA Open Source (2.8.14) finden Sie unter:
Link: https://rasa.com/docs/rasa/2.x/installation

Compatibility Matrix:
Link: https://rasa.com/docs/rasa-enterprise/changelog/compatibility-matrix/




## 4. Beschreibung der Inhalte der einzelnen Dateien:
***
Alle Informationen zu den einzelnen Dateien sind der Arbeit bzw. den Kommentaren im Code zu entnehmen.



## 5. Integration auf einer Website:
***
Im Projekt ist eine index.html zu finden, die den Code zur Integration des Chatbots auf einer Website beschreibt.
Um den Chatbot lokal zu öffnen sind folgende Schritte notwendig:

    1) Aenderungen der credentials.yml Datei:

        socketio:
            user_message_evt: user_uttered
            bot_message_evt: bot_uttered
            session_persistence: true

    2) API im Terminal zulassen - Befehlt im Terminal:

        rasa run -m models --enable-api --cors "*"


    3) Öffnen der index.html Datei im Browser