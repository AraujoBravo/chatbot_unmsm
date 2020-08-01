# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import sqlite3

from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk import Action, Tracker
from typing import Any, Dict, List, Text
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.events import AllSlotsReset


class InfoAdministrativeForm(FormAction):

    def name(self):
        return "tramite_doc_form"

    @staticmethod
    def required_slots(tracker):
        return [
            "documento",
            "facultad",
            "tipo",
        ]

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:

        documento = tracker.get_slot("documento")
        facultad = tracker.get_slot("facultad")
        tipo = tracker.get_slot("tipo")
        try:
            con = sqlite3.connect('db_unmsm.sqlite3')
            cursor = con.cursor()
            cursor2 = con.cursor()
            cursor.execute(
                """ select
                        a.id,
                        a.codigo,
                        a.monto
                    from
                        (
                        select
                            ap.id_administrativeprocedures id,
                            case
                                WHEN substr(ap.code_bank, 1, 3) = '207' then 'POSGRADO'
                                WHEN substr(ap.code_bank, 1, 3) = '206' then 'OCA'
                                ELSE 'PREGRADO' 
                            end tipo,
                            ap.denomination tramite,
                            ap.code_bank codigo,
                            ap.payment monto
                        from
                            administrative_procedures ap
                        inner join administrative_procedures_denomination_global apg on
                            ap.denomination_global_id = apg.id_denominationglobal
                        where
                            ap.code_bank != '-') a
                    where
                        a.tipo = ?
                        and a.tramite like ? """, (str.upper(tipo), f"{str.upper(documento)}%"))

            resultado = cursor.fetchone()

            if resultado is not None:
                id_tramite = resultado[0]
                codigo_pago = resultado[1]
                monto_pago = resultado[2]

                cursor2.execute(
                    """ select 
                            apr.description,
                            apr.code_bank codigo,
                            apr.payment monto 
                        from administrative_procedures_request apr 
                        where apr.administration_procedures_id = ? """, (id_tramite,))

                resultado_requisitos = cursor2.fetchall()

                mensaje_requisitos = "Lista de requisitos:\n"
                if resultado_requisitos is not None:
                    count = 0
                    for fila in resultado_requisitos:
                        count += 1
                        descripcion = fila[0]
                        codigo = fila[1]
                        monto = fila[2]
                        if codigo is not '-':
                            mensaje_requisitos += f"{count}. {descripcion} -> código: {codigo}, monto: {monto}\n"
                        else:
                            mensaje_requisitos += f"{count}. {descripcion}\n"

                if len(codigo_pago) == 6:
                    dispatcher.utter_message(
                        f"Debe realizar un deposito en el Banco Pichincha al codigo {codigo_pago} la cantidad de S/ "
                        f"{monto_pago}.\n{mensaje_requisitos}")
                elif len(codigo_pago) == 3:
                    dispatcher.utter_message(
                        f"Debe realizar un deposito en el Banco Pichincha al codigo 210-{codigo_pago} la cantidad de "
                        f"S/ {monto_pago}.\n{mensaje_requisitos}")
                else:
                    dispatcher.utter_message(f"El tramite es gratuito, no tiene que realizar ningun pago.\n{mensaje_requisitos}")
            else:
                dispatcher.utter_message("No se encontro informacion sobre la consulta, derivaremos su consulta")

        except sqlite3.Error:
            dispatcher.utter_message("No se encontro informacion sobre la consulta, derivaremos su consulta")
        finally:
            try:
                cursor.close()
            except:
                pass
            try:
                cursor2.close()
            except:
                pass
            try:
                con.close()
            except:
                pass

        return [AllSlotsReset()]


class ActionSaludoUsuario(Action):
    """Revertible mapped action for utter_greet"""

    def name(self):
        return "action_saludo"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_template("utter_saludo", tracker)
        return [UserUtteranceReverted()]
