# Diese Datei beinhaltet alle Costum Actions (Python) die durch den Chatbot aufgerufen werden können
# Hierzu zählen: 
# 1) Begruessung des Users
# 2) Default-Fallback
# 3) QueryDatabase - Eingrenzungen der Suche durch den User
# 4) QueryDatabase - ohne Eingrenzungen der Suche 
# 5) QueryDatabase - Alle Ergebnisse ausgeben
# 6) Speicherung der Konversation
# 7) Speicherung Bewertung von Selbstlernmaterialien


# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from cgitb import text
import datetime as dt


from csv import writer


import sqlite3
from sqlite3 import Error

import random


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


# 1) Begruessung des Users
# Diese Klasse beinhaltet die Begrüßung die durch eine Begrüßung des Users initialisiert wird.
# Dabei werden drei Antworten ausgegeben: Begrüßung, Vorstellung und Frage wie weitergeholfen werden kann.
class BegruessungUser(Action):
    def name(self) -> Text:
        return "action_begruessung_user"

    def run(self, dispatcher: CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict[Text,Any]]:
        
        dispatcher.utter_message(text="Hi, ich bin TED! Der Chatbot zum TEgoDi Projekt.")
        dispatcher.utter_message(text="Ich bin dazu da, dir deine Fragen rund um das Projekt TEgoDi zu beantworten sowie dich bei der Suche nach Selbstlernmaterialien zu unterstützen.")
        dispatcher.utter_message(text="Hast du eine allgemeine Frage zum Projekt oder suchst du nach Selbstlernmaterialien?")
        
        return []



# 2) Default-Fallback
# Die nachfolgenden zwei Klassen dienen zur Beschreibung der Fallback-Schleife.
# ActionDefaultFallback: erste Eingabe wird nicht verstanden
# ActionDefaultFallbackColilab: Human Handover
# --> also das was passiert, wenn eine Eingabe nicht verstanden wird.
# Hilfestellung: https://rasa.com/docs/rasa/fallback-handoff/

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher, tracker, domain):


        message = "Es tut mir leid. Ich habe leider deine Nachricht nicht verstanden. :( Könntest du deine Eingabe umformulieren?"
        dispatcher.utter_message(text=message)

        return []


class ActionDefaultFallbackColilab(Action):
    def name(self) -> Text:
        return "action_default_mail_colilab"

    def run(self,dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         dispatcher.utter_message(text="Sorry, ich habe deine Eingabe leider nochmals nicht verstanden. Wende dich doch mit deinem Anliegen per Mail an das TEgoDi-Team mit folgender E-Mail Adresse:")        
         dispatcher.utter_message(text="colilab@ph-weingarten.de")        
        
        
         return []






# 3) QueryDatabase - Eingrenzungen der Suche durch den User
# Durchsuchung der SQLite Datenbank mit den jeweiligen Eingrenzungen
# Beispielcode: https://github.com/rctatman/personal_website_bot/blob/main/actions/actions.py
#               https://www.python-lernen.de/csv-datei-einlesen.htm

class QueryDatabase(Action):

     def name(self) -> Text:
         return "action_query_datebase"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         """
         datebase: Pfad Speicherort
         Übergabe der Eingrezung vom User über die einzelnen Slots
         Aufruf der einzelnen Methoden
         dispatcher: Rückgabe des Ergbnis im Chatfenster
         """
         database = r"/Users/julianbrandle/Desktop/Rasa/testumgebung61/edu_db/selbstlernmaterialien.db"
         conn = QueryDatabaseMethods.create_connection(database)
         slot_value = tracker.get_slot("resource_wissensgebiet")
         slot_value_format = tracker.get_slot("resource_format")         
         slot_value_kompetenz = tracker.get_slot("resource_kompetenz")
         slot_value_themenbereich = tracker.get_slot("resource_themenbereich")

         get_query_results = QueryDatabaseMethods.select_all_tasks(conn=conn, slot_value=slot_value, slot_value_format=slot_value_format ,slot_value_kompetenz=slot_value_kompetenz, slot_value_themenbereich=slot_value_themenbereich)
         return_text = QueryDatabaseMethods.main(get_query_results)


         dispatcher.utter_message(text=str(return_text))

         return []


class QueryDatabaseMethods:
    def create_connection(db_file):
        """ Aufbau Verbindung mit SQLite Datenbank
            Rückgabe ob Verbindung aufgebaut werden konnte oder nicht
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn



    
    def select_all_tasks(conn, slot_value, slot_value_format, slot_value_kompetenz, slot_value_themenbereich):
        """
        Durchsuchung aller Zeilen:
        je nachdem welche Eingrenzungen/Slots vom User angegeben wurde
        wird die jeweilige Abfrage ausgewählt
        Rückgabe: mehrdimensionale Liste
        """
        cur = conn.cursor()
        
        if (slot_value) is (slot_value):
        
            cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value}"''')
            rows = cur.fetchall()
            return(rows)

        elif (slot_value + slot_value_format) is (slot_value + slot_value_format):

            cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value} AND format="{slot_value_format}"''')
            rows = cur.fetchall()
            return(rows)


        elif (slot_value + slot_value_kompetenz) is (slot_value + slot_value_kompetenz):
            cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value} AND kompetenz="{slot_value_kompetenz}"''')
            rows = cur.fetchall()
            return(rows)


        elif (slot_value + slot_value_themenbereich) is (slot_value + slot_value_themenbereich):
            cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value} AND themenbereich="{slot_value_themenbereich}"''')
            rows = cur.fetchall()
            return(rows)


    def main(rows):
        """
        Verarbeitung der mehrdimensionale Liste
        auf der Grundlage wie viele Ergebnisse gefunden wurden
        bei mehr als drei Ergebnissen: zufällige Auswahl der Ergebnisse
        Sicherstellung das es sich dennoch nicht um die drei gleichen Ergebnisse handelt
        """
        if len(list(rows)) < 1:
            return "Leider habe ich keine Selbstlernmaterialien zu diesem Thema gefunden"

        elif len(list(rows)) <= 3:
            return f"Folgende drei Selbstlernmaterialien habe ich gefunden:\nTitel: {(rows[0][0])} Verfügbar unter: {(rows[0][4])} \nTitel: {(rows[1][0])} Verfügbar unter: {(rows[1][4])} \nTitel: {(rows[2][0])} Verfügbar unter: {(rows[2][4])}"

        else:
            a = len((rows))
            auswahl_index_a = random.uniform(0, a)
            ausgabe_a = (int(auswahl_index_a))

            auswahl_index_b = random.uniform(0, a)
            while auswahl_index_b == auswahl_index_a:
                auswahl_index_b = random.uniform(0,a)
            ausgabe_b = (int(auswahl_index_b))

            auswahl_index_c = random.uniform(0, a)
            while auswahl_index_c == auswahl_index_a:
                auswahl_index_c = random.uniform(0,a)
            while auswahl_index_c == auswahl_index_b:
                auswahl_index_c = random.uniform(0,a)            
            ausgabe_c = (int(auswahl_index_c))

            return f"""Ich habe einige Materialien dazu gefunden. Hier eine Auswahl:\nTitel: {(rows[ausgabe_a][0])} Verfügbar unter: {(rows[ausgabe_a][4])}\nTitel: {(rows[ausgabe_b][0])} Verfügbar unter: {(rows[ausgabe_b][4])}\nTitel: {(rows[ausgabe_c][0])} Verfügbar unter: {(rows[ausgabe_c][4])}"""




# 4) QueryDatabase - ohne Eingrenzungen der Suche 
# Das Selbe wie oben, ohne Eingrenzung
# Bislang keine Möglichkeit gefunden, dies in QueryDatabase zu integrieren

class QueryDatabase_ohne_eingrenzung(Action):

     def name(self) -> Text:
         return "action_query_database_ohne_eingrenzung"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         database = r"/Users/julianbrandle/Desktop/Rasa/testumgebung61/edu_db/selbstlernmaterialien.db"
         conn = QueryDatabaseMethodsNoFilter.create_connection(database)
         slot_value = tracker.get_slot("resource_wissensgebiet")

         get_query_results = QueryDatabaseMethodsNoFilter.select_all_tasks_no_filter(conn=conn, slot_value=slot_value)
         return_text = QueryDatabaseMethodsNoFilter.main_no_filter(get_query_results)


         dispatcher.utter_message(text=str(return_text))

         return []



class QueryDatabaseMethodsNoFilter:
    def create_connection(db_file):

        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn




    def select_all_tasks_no_filter(conn, slot_value):

        cur = conn.cursor()
        cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value}"''')

        ergebnisse = cur.fetchall()

        return(ergebnisse)



    def main_no_filter(ergebnisse):

        if len(list(ergebnisse)) < 1:
            return "Leider habe ich keine Selbstlernmaterialien zu diesem Thema gefunden"

        elif len(list(ergebnisse)) <= 3:
            return f"Folgende drei Selbstlernmaterialien habe ich gefunden:\nTitel: {(ergebnisse[0][0])} Verfügbar unter: {(ergebnisse[0][4])} \nTitel: {(ergebnisse[1][0])} Verfügbar unter: {(ergebnisse[1][4])} \nTitel: {(ergebnisse[2][0])} Verfügbar unter: {(ergebnisse[2][4])}"

        else:
            a = len((ergebnisse))
            auswahl_index_a = random.uniform(0, a)
            ausgabe_1 = (int(auswahl_index_a))

            auswahl_index_b = random.uniform(0, a)
            while auswahl_index_b == auswahl_index_a:
                auswahl_index_b = random.uniform(0,a)
            ausgabe_2 = (int(auswahl_index_b))

            auswahl_index_c = random.uniform(0, a)
            while auswahl_index_c == auswahl_index_a:
                auswahl_index_c = random.uniform(0,a)
            while auswahl_index_c == auswahl_index_b:
                auswahl_index_c = random.uniform(0,a)            
            ausgabe_3 = (int(auswahl_index_c))

            return f"""Ich habe einige Materialien dazu gefunden. Hier eine Auswahl:\nTitel: {(ergebnisse[ausgabe_1][0])} Verfügbar unter: {(ergebnisse[ausgabe_1][4])}\nTitel: {(ergebnisse[ausgabe_2][0])} Verfügbar unter: {(ergebnisse[ausgabe_2][4])}\nTitel: {(ergebnisse[ausgabe_3][0])} Verfügbar unter: {(ergebnisse[ausgabe_3][4])}"""




# 5) QueryDatabase - Alle Ergebnisse ausgeben
# Selbe Methode wie oben um alle Ergebnisse anzuzeigen, wenn bereits drei Ergebnisse ausgegeben wurden
# Fehlende Umsetzung einer geeigneten Darstellung der Ergbnisse 
# Bislang Rückgabe der unveränderten mehrdimensionalen Liste

class QueryDatabase(Action):

     def name(self) -> Text:
         return "action_query_datebase_alle_Ergebnisse_anzeigen"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         database = r"/Users/julianbrandle/Desktop/Rasa/testumgebung61/edu_db/selbstlernmaterialien.db"
         conn = QueryDatabaseMethodsAlleErgebnisseSuche.create_connection(database)
         slot_value = tracker.get_slot("resource_wissensgebiet")
         slot_value_format = tracker.get_slot("resource_format")         
         slot_value_kompetenz = tracker.get_slot("resource_kompetenz")
         slot_value_themenbereich = tracker.get_slot("resource_themenbereich")

         get_query_results = QueryDatabaseMethodsAlleErgebnisseSuche.select_all_tasks_alle_ergebnisse_Suche(conn=conn, slot_value=slot_value, slot_value_format=slot_value_format ,slot_value_kompetenz=slot_value_kompetenz, slot_value_themenbereich=slot_value_themenbereich)
         return_text = QueryDatabaseMethodsAlleErgebnisseSuche.main_alle_Ergebnisse_der_Suche(get_query_results)


         dispatcher.utter_message(text=str(return_text))

         return []



class QueryDatabaseMethodsAlleErgebnisseSuche:
    def create_connection(db_file):
        """ Aufbau Verbindung mit SQLite Datenbank
            Rückgabe ob Verbindung aufgebaut werden konnte oder nicht
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        return conn


    def select_all_tasks_alle_ergebnisse_Suche(conn, slot_value, slot_value_format, slot_value_kompetenz, slot_value_themenbereich):
        """
        Query all rows in the tasks table
        :param conn: the Connection object
        :return:
        """
        cur = conn.cursor()
        
        if (slot_value) is (slot_value):
        
            cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value}"''')
            rows = cur.fetchall()
            return(rows)

        elif (slot_value + slot_value_format) is (slot_value + slot_value_format):

            cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value} AND format="{slot_value_format}"''')
            rows = cur.fetchall()
            return(rows)


        elif (slot_value + slot_value_kompetenz) is (slot_value + slot_value_kompetenz):
            cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value} AND kompetenz="{slot_value_kompetenz}"''')
            rows = cur.fetchall()
            return(rows)


        elif (slot_value + slot_value_themenbereich) is (slot_value + slot_value_themenbereich):
            cur.execute(f'''SELECT * FROM selbstlernmaterialien WHERE wissensgebiet="{slot_value} AND themenbereich="{slot_value_themenbereich}"''')
            rows = cur.fetchall()
            return(rows)


    def main_alle_Ergebnisse_der_Suche(rows):

    
        if len(list(rows)) < 1:
            return "Leider habe ich keine Selbstlernmaterialien zu diesem Thema gefunden"

        else:
            for row in rows:
                return rows




# 6) Speicherung der Konversation
# Speicherung einer Konversation mit der Verabschiedung durch den User 
# Ausgabe der Verabschiedung des Users
# Quelle:  https://github.com/ashus3868/RasaConversationToCSVTXT
#          https://www.youtube.com/watch?v=fvFyWzy1A3Y

class ActionSaveConversation(Action):

    def name(self) -> Text:
        return "action_konversation_sichern"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        conversation=tracker.events
        print(conversation)
        import os
        if not os.path.isfile('sammlung_aller_chatverläufe.csv'):
            with open('sammlung_chatverlauf.csv','w') as file:
                file.write("intent;benutzereingabe;entity_name;entity_value;titel_ausgegebenener_action;antwort_chatbots\n")
        chat_data=''
        for i in conversation:
            if i['event'] == 'user':
                chat_data+=i['parse_data']['intent']['name']+';'+i['text']+';'
                print('user: {}'.format(i['text']))
                if len(i['parse_data']['entities']) > 0:
                    chat_data+=i['parse_data']['entities'][0]['entity']+';'+i['parse_data']['entities'][0]['value']+';'
                    print('extra data:', i['parse_data']['entities'][0]['entity'], '=',
                          i['parse_data']['entities'][0]['value'])
                else:
                    chat_data+=";"
            elif i['event'] == 'bot':
                print('Bot: {}'.format(i['text']))
                try:
                    chat_data+=i['metadata']['utter_action']+';'+i['text']+'\n'
                except KeyError:
                    pass
        else:
            with open('sammlung_chatverlauf.csv','a') as file:
                file.write(chat_data)

        dispatcher.utter_message(text="Ich wünsche dir noch einen schönen Tag und viel Erfolg bei deinem Projekt.")
        dispatcher.utter_message(text="Und zöger nicht, mich um Hilfe zu bitten. Bis bald!")

        return []




# 7) Speicherung Bewertung von Selbstlernmaterialien
# Prototypische Umsetzung derSpeicherung einer Bewertung von Selbstlernmaterialien
# mit Titel des Selbstlernmaterialies und Bewertung in Sterne

class BewertungSelbstlernmaterialinCsv(Action):

     def name(self) -> Text:
         return "bewertung_sterne_in_csv_ubertragen"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
         
         datum_uhrzeit = dt.datetime.now()
         slot_value_titel_selbstlernmaterial = tracker.get_slot("titel_selbstlernmaterial")         
         slot_bewertung_in_sterne = tracker.get_slot("bewertung_in_sterne")
         
         neue_reihe = (datum_uhrzeit, slot_value_titel_selbstlernmaterial, slot_bewertung_in_sterne)

         with open('bewertung_selbstlernmaterialien.csv', 'a', newline='') as f_object:  
            writer_object = writer(f_object)
            writer_object.writerow(neue_reihe)  
            f_object.close()
        


         return []


