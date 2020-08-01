## gracias
* gracias
  - utter_de_nada

## adios
* adios
  - utter_adios
  
## Preguntas frecuentes
* faq
  - respond_faq

## info tramite documentario
* info_tramite_doc
  - tramite_doc_form                   <!--Run the sales_form action-->
  - form{"name": "tramite_doc_form"}   <!--Activate the form-->
  - form{"name": null}                 <!--Deactivate the form-->

## info tramite documentario, interrupt faq
* info_tramite_doc
    - tramite_doc_form
    - form{"name": "tramite_doc_form"}
* faq
    - respond_faq
    - tramite_doc_form
    - form{"name": null}

# el bot no entendio, fuera de contexto
* out_of_scope
  - utter_out_of_scope