```mermaid
graph TD
    %% Define Styles
    classDef frontend fill:#61dafb,stroke:#333,stroke-width:2px,color:#000;
    classDef backend fill:#009688,stroke:#333,stroke-width:2px,color:#fff;
    classDef database fill:#336791,stroke:#333,stroke-width:2px,color:#fff;
    classDef external fill:#3ECF8E,stroke:#333,stroke-width:2px,color:#000;

    %% Frontend Tier
    subgraph Client ["Frontend (React + Vite)"]
        direction TB
        UI_Student[Student View]
        UI_Teacher[Teacher View]
        Auth_Client[Supabase Auth Client]
        API_Client[API Client / Fetch]
        
        UI_Student --> API_Client
        UI_Teacher --> API_Client
        UI_Student -.-> Auth_Client
        UI_Teacher -.-> Auth_Client
    end

    %% Backend Tier
    subgraph Server ["Backend (FastAPI)"]
        direction TB
        Auth_Middleware{Auth Middleware<br/>Verify JWT & Role}
        
        subgraph Routes ["API Routes"]
            Route_Courses[GET /courses]
            Route_Classes_Get[GET /classes]
            Route_Classes_Post[POST /classes<br/>Teacher Only]
            Route_Register[POST /classes/id/register<br/>Student Only]
        end
        
        subgraph ORM ["Data Access (SQLAlchemy)"]
            Models[Models: Course, Class]
        end
        
        API_Client -->|HTTP Requests with JWT| Auth_Middleware
        Auth_Middleware --> Routes
        Routes --> ORM
    end

    %% Database Tier
    subgraph DB ["Database (PostgreSQL / Supabase)"]
        direction TB
        Table_Courses[(courses)]
        Table_Classes[(classes)]
        Table_Profiles[(profiles / auth.users)]
        
        Models -->|SQL over TCP| Table_Courses
        Models -->|SQL over TCP| Table_Classes
    end

    %% External Auth
    subgraph Supabase ["Supabase Auth Service"]
        Auth_Server[Auth API]
    end

    %% Cross-tier Connections
    Auth_Client -->|Login/Register| Auth_Server
    Auth_Server -.->|Returns JWT| Auth_Client
    Auth_Middleware -.->|Verify Token| Auth_Server
    
    %% Apply Styles
    class UI_Student,UI_Teacher,Auth_Client,API_Client frontend;
    class Auth_Middleware,Route_Courses,Route_Classes_Get,Route_Classes_Post,Route_Register,Models backend;
    class Table_Courses,Table_Classes,Table_Profiles database;
    class Auth_Server external;
    ```