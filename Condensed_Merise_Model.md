# Modèle Merise condensé adapté à la structure réelle

flowchart TD
    PDFDocument[Documents PDF] -->|Extraction| NLP[Traitement NLP]
    NLP --> KnowledgeBase[Base de Connaissances]
    KnowledgeBase --> FAQGen[FAQ Générée]
    FAQGen --> AdminValidation[Validation Admin]
    AdminValidation --> FAQVal[FAQ Validée]
    
    Visitor[Visiteurs] -->|Consultation| FAQVal
    Visitor -->|Log| VisitLog[Analyse Visites]
    VisitLog --> Prediction[Prédictions ML]
    
    Admin[Admin] -->|Gestion| FAQVal
    Admin -->|Configuration| NLP
    Admin -->|Monitoring| Prediction
    
    subgraph BDD
        User
        FAQ
        PDFDocument
        VisitLog
        AdminActionLog
        PredictionModel
    end

    Admin -->|Actions| AdminActionLog
    FAQVal -->|Création/Validation| Admin
    FAQGen -->|Ajout| FAQ
    PDFDocument -->|Indexation| KnowledgeBase
    VisitLog -->|Stockage| BDD
    Prediction -->|Stockage| PredictionModel
