                                                                                
 Usage: dagify [OPTIONS] COMMAND [ARGS]...                                      
                                                                                
 CLI for dagify                                                                 
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ compose   Creates a new workflow from a description, supporting different    │
│           types of workflow representations.                                 │
│ refine    Refines an existing workflow by improving metadata, details,       │
│           instructions and tags. Can also apply agent tags to enable agentic │
│           execution of workflow steps.                                       │
│ resolve   Executes one pass of AI-assisted refinement to upgrade the DAG to  │
│           a more concrete type, while respecting the defined type hierarchy  │
│           floor.                                                             │
│ compile   Compiles a DAG into an executable format.                          │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: dagent [OPTIONS] COMMAND [ARGS]...                                      
                                                                                
 CLI for dagent                                                                 
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ validate     Validates the correctness of a DAG by checking its structure,   │
│              dependencies, and execution feasibility.                        │
│ optimize     Optimizes AI-driven DAG nodes (e.g., prompts, spec stages) to   │
│              improve accuracy and reliability by tuning them against a       │
│              provided test dataset.                                          │
│ execute      Execute a DAG plan with structured input and AI-assisted        │
│              processing.                                                     │
│ interpret    Generates a DAG plan dynamically and executes it immediately.   │
│ synthesize   Generates a DAG plan, compiles it to executable code, and       │
│              executes it.                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: schemagin [OPTIONS] COMMAND [ARGS]...                                   
                                                                                
 CLI for schemagin                                                              
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ compose     Generate a completely new schema from scratch using              │
│             natural‑language prompts. Ideal for quickly scaffolding new      │
│             projects or ideas.                                               │
│ refine      Iteratively improve or extend an existing schema. Accepts        │
│             structured schema definitions from files, stdin, or explicit     │
│             database links as context.                                       │
│ visualize   Render schema diagrams in various formats and optionally export  │
│             the schema concurrently.                                         │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: datagin [OPTIONS] COMMAND [ARGS]...                                     
                                                                                
 CLI for datagin                                                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ ingest       Extract and structure data from an input source.                │
│ synthesize   Generate synthetic data based on schema and prompt.             │
│ transform    Transform structured data between schemas.                      │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: dagify compose [OPTIONS] PROMPT [DATA]                                  
                                                                                
 Creates a new workflow from a description, supporting different types of       
 workflow representations.                                                      
 Examples:                                                                      
     1. Create a new DAG from a description:                                    
        $ dagify compose "Extract data from API, transform, and load to         
 database"                                                                      
                                                                                
 2. Create a DAG using an existing workflow as reference:        $ dagify       
 compose "Create CI pipeline" reference_workflow.json                           
 3. Create a DAG using piped input as reference:        $ cat                   
 reference_workflow.json | dagify compose "Optimize this workflow" -            
 4. Create a DAG from a database schema:        $ dagify compose "Generate ETL  
 pipeline" "postgres://user:pass@localhost:5432/db"                             
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT    Description of the process or workflow to generate  │
│                          a DAG for                                           │
│                          [default: None]                                     │
│                          [required]                                          │
│      data        [DATA]  DAG source - can be a JSON file, agilink URI, JSON  │
│                          string, or database connection. Use '-' for stdin   │
│                          [default: None]                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --type                            TEXT     Type of DAG to generate           │
│                                            (plain_text, typed, spec, stub,   │
│                                            shim, pure)                       │
│                                            [default: typed]                  │
│ --intelligence                    INTEGER  Intelligence level (0-100) for    │
│                                            AI-assisted DAG generation        │
│                                            [default: 0]                      │
│ --seed                            INTEGER  Seed for deterministic workflow   │
│                                            generation                        │
│ --format                          TEXT     Format for DAG output (yaml,      │
│                                            json)                             │
│                                            [default: yaml]                   │
│ --visual                          TEXT     Format(s) for DAG visualization   │
│                                            (d2, graphviz, ascii)             │
│ --ascii           --no-ascii               Show ASCII visualization of the   │
│                                            generated DAG                     │
│                                            [default: no-ascii]               │
│ --output-dir                      TEXT     Directory to save the generated   │
│                                            DAG and visualization             │
│                                            [default: ./outputs/dagify/]      │
│ --verbose         --no-verbose             Enable verbose output             │
│                                            [default: no-verbose]             │
│ --help                                     Show this message and exit.       │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: dagify refine [OPTIONS] PROMPT [DATA]                                   
                                                                                
 Refines an existing workflow by improving metadata, details, instructions and  
 tags. Can also apply agent tags to enable agentic execution of workflow steps. 
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT    Description of the refinement to be applied         │
│                          [default: None]                                     │
│                          [required]                                          │
│      data        [DATA]  DAG source - can be a JSON file, agilink URI, or    │
│                          JSON string. Use '-' for stdin                      │
│                          [default: None]                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --intelligence                         INTEGER  Intelligence level (0-100)   │
│                                                 for AI-assisted DAG          │
│                                                 generation                   │
│                                                 [default: 0]                 │
│ --seed                                 INTEGER  Seed for deterministic       │
│                                                 workflow generation          │
│ --format                               TEXT     Format for DAG output (yaml, │
│                                                 json)                        │
│                                                 [default: yaml]              │
│ --visual                               TEXT     Format(s) for DAG            │
│                                                 visualization (d2, graphviz, │
│                                                 ascii)                       │
│ --ascii           --no-ascii                    Display ASCII visualization  │
│                                                 of the generated DAG         │
│                                                 [default: no-ascii]          │
│ --output-dir                           TEXT     Directory to save the        │
│                                                 refined DAG and viz          │
│ --verbose         --no-verbose                  Enable verbose output        │
│                                                 [default: no-verbose]        │
│ --yaml-display    --no-yaml-display             Display YAML representation  │
│                                                 of the DAG in console when   │
│                                                 not piped                    │
│                                                 [default: no-yaml-display]   │
│ --help                                          Show this message and exit.  │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: dagify resolve [OPTIONS] DATA                                           
                                                                                
 Executes one pass of AI-assisted refinement to upgrade the DAG to a more       
 concrete type, while respecting the defined type hierarchy floor.              
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    data      TEXT  The DAG to resolve (file path, JSON string, or agilink  │
│                      URI)                                                    │
│                      [default: None]                                         │
│                      [required]                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --intelligence                         INTEGER  Intelligence level (0-100)   │
│                                                 for AI-assisted DAG          │
│                                                 generation                   │
│                                                 [default: 0]                 │
│ --seed                                 INTEGER  Seed for deterministic       │
│                                                 workflow generation          │
│ --format                               TEXT     Format for DAG output (yaml, │
│                                                 json)                        │
│                                                 [default: yaml]              │
│ --visual                               TEXT     Format(s) for DAG            │
│                                                 visualization (d2, graphviz, │
│                                                 ascii)                       │
│ --ascii           --no-ascii                    Show ASCII visualization of  │
│                                                 the generated DAG            │
│                                                 [default: no-ascii]          │
│ --output-dir                           TEXT     Directory to save the        │
│                                                 resolved DAG and viz         │
│ --verbose         --no-verbose                  Enable verbose output        │
│                                                 [default: no-verbose]        │
│ --yaml-display    --no-yaml-display             Display YAML representation  │
│                                                 of the DAG in console when   │
│                                                 not piped                    │
│                                                 [default: no-yaml-display]   │
│ --help                                          Show this message and exit.  │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: dagify compile [OPTIONS] [DATA]                                         
                                                                                
 Compiles a DAG into an executable format.                                      
 The compilation process involves two steps: 1. Resolving the DAG to the        
 specified type floor 2. (Optional) Converting to a target format               
 If no build target is specified, outputs the resolved DAG in YAML format.      
 Examples:                                                                      
     # Resolve to 'typed' (default) and output YAML                             
     dagify compile typed_dag.yaml --output-dir ./outputs/dagify                
                                                                                
 # Resolve to 'spec' and compile to 'crewai' format     dagify compile          
 spec_dag.json --type-floor spec --build-target crewai                          
 # Compile from stdin to 'crewai-flat'     cat typed_dag.yaml | dagify compile  
 - --build-target crewai-flat > crew.py                                         
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   data      [DATA]  The DAG to compile (file path, JSON string, or agilink   │
│                     URI). Use '-' for stdin                                  │
│                     [default: None]                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --type-floor                      TEXT     Minimum DAG type to resolve to    │
│                                            before compilation                │
│                                            [default: typed]                  │
│ --build-target                    TEXT     Target format for compilation     │
│                                            (crewai, crewai-flat, langchain,  │
│                                            wdl, or wdl-shims)                │
│ --output-dir                      TEXT     Base directory for DAG outputs    │
│                                            [default: ./outputs/dagify]       │
│ --ascii           --no-ascii               Show ASCII visualization of the   │
│                                            generated DAG                     │
│                                            [default: no-ascii]               │
│ --intelligence                    INTEGER  Intelligence level (0-100) for    │
│                                            AI-assisted compilation           │
│                                            [default: 0]                      │
│ --verbose         --no-verbose             Enable verbose output             │
│                                            [default: no-verbose]             │
│ --help                                     Show this message and exit.       │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: dagent execute [OPTIONS] [PLAN] [DATA]                                  
                                                                                
 Execute a DAG plan with structured input and AI-assisted processing.           
 Saves the full execution results to a file in the output directory. Displays   
 final node outputs to stderr. Pipes full results to stdout if requested.       
 Examples:                                                                      
     # Execute from YAML file and save results to                               
 ./outputs/dagent/workflow/execution_results/                                   
     dagent execute workflow.yaml --output-dir ./outputs/dagent/                
                                                                                
 # Execute from JSON file with external data     dagent execute plan.json       
 data.csv                                                                       
 # Execute from stdin     cat my_dag.json | dagent execute -                    
 # Execute a CrewAI project in the current directory     dagent execute .       
 # Execute a specific CrewAI project directory     dagent execute               
 ./my_crewai_project/ --data input_vars.json                                    
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│   plan      [PLAN]  DAG plan to execute. Can be a JSON file, agilink URI, or │
│                     JSON string. Use '-' for stdin                           │
│                     [default: None]                                          │
│   data      [DATA]  External data to provide during execution                │
│                     [default: None]                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --jit                              TEXT     Just-in-time (JIT) refinement    │
│                                             mode                             │
│ --tools                            TEXT     Comma-separated list of CLI      │
│                                             tools available in the runtime   │
│ --tools-file                       TEXT     File containing a list of tools  │
│                                             (one per line)                   │
│ --output-format                    TEXT     Format for execution results     │
│                                             (yaml, json)                     │
│                                             [default: yaml]                  │
│ --output-dir                       TEXT     Base directory to save execution │
│                                             results                          │
│                                             [default: ./outputs/dagent/]     │
│ --intelligence                     INTEGER  Intelligence level (0-100) to    │
│                                             determine model selection        │
│                                             [default: 0]                     │
│ --seed                             INTEGER  Seed for deterministic execution │
│ --verbose          --no-verbose             Enable verbose output            │
│                                             [default: no-verbose]            │
│ --help                                      Show this message and exit.      │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: schemagin compose [OPTIONS] PROMPT                                      
                                                                                
 Generate a completely new schema from scratch using natural‑language prompts.  
 Ideal for quickly scaffolding new projects or ideas.                           
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT  Natural language description of the schema to         │
│                        generate.                                             │
│                        [default: None]                                       │
│                        [required]                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --format                                     TEXT     Output format for the  │
│                                                       schema.                │
│                                                       [default: yaml]        │
│ --visual                                     TEXT     Generate               │
│                                                       visualizations in      │
│                                                       specified formats. Can │
│                                                       be specified multiple  │
│                                                       times.                 │
│ --ascii              --no-ascii                       Display ASCII          │
│                                                       visualization of the   │
│                                                       schema.                │
│                                                       [default: no-ascii]    │
│ --output-dir                                 TEXT     Base output directory  │
│                                                       path. Defaults to      │
│                                                       outputs/schemagin/. A  │
│                                                       unique subdirectory    │
│                                                       will be created        │
│                                                       inside.                │
│                                                       [default:              │
│                                                       outputs/schemagin]     │
│ --intelligence                               INTEGER  Intelligence level.    │
│                                                       0-100                  │
│                                                       [default: 0]           │
│ --seed                                       INTEGER  Set a seed value for   │
│                                                       deterministic schema   │
│                                                       generation.            │
│ --no-foreign-keys    --no-no-foreign-keys             Disable foreign key    │
│                                                       constraints in the     │
│                                                       generated schema.      │
│                                                       [default:              │
│                                                       no-no-foreign-keys]    │
│ --verbose            --no-verbose                     Show additional debug  │
│                                                       information.           │
│                                                       [default: no-verbose]  │
│ --quiet              --no-quiet                       Suppress all output    │
│                                                       except critical        │
│                                                       errors.                │
│                                                       [default: no-quiet]    │
│ --help                                                Show this message and  │
│                                                       exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: schemagin refine [OPTIONS] PROMPT                                       
                                                                                
 Iteratively improve or extend an existing schema. Accepts structured schema    
 definitions from files, stdin, or explicit database links as context.          
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT  Natural language description of the refinements to    │
│                        make.                                                 │
│                        [default: None]                                       │
│                        [required]                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --context                                   TEXT     Path to existing     │
│                                                         schema file, '-' for │
│                                                         stdin, or agilink:// │
│                                                         URI                  │
│                                                         [required]           │
│    --format                                    TEXT     Output format for    │
│                                                         the schema.          │
│                                                         [default: yaml]      │
│    --visual                                    TEXT     Generate             │
│                                                         visualizations in    │
│                                                         specified formats.   │
│                                                         Can be specified     │
│                                                         multiple times.      │
│    --ascii              --no-ascii                      Display ASCII        │
│                                                         visualization of the │
│                                                         schema.              │
│                                                         [default: no-ascii]  │
│    --output-dir                                TEXT     Base output          │
│                                                         directory path.      │
│                                                         Defaults to          │
│                                                         outputs/schemagin/.  │
│                                                         A unique             │
│                                                         subdirectory will be │
│                                                         created inside.      │
│                                                         [default:            │
│                                                         outputs/schemagin]   │
│    --intelligence                              INTEGER  Intelligence level.  │
│                                                         0-100                │
│                                                         [default: 0]         │
│    --seed                                      INTEGER  Set a seed value for │
│                                                         deterministic schema │
│                                                         generation.          │
│    --no-foreign-keys    --no-no-foreign-ke…             Disable foreign key  │
│                                                         constraints in the   │
│                                                         generated schema.    │
│                                                         [default:            │
│                                                         no-no-foreign-keys]  │
│    --verbose            --no-verbose                    Show additional      │
│                                                         debug information.   │
│                                                         [default:            │
│                                                         no-verbose]          │
│    --quiet              --no-quiet                      Suppress all output  │
│                                                         except critical      │
│                                                         errors.              │
│                                                         [default: no-quiet]  │
│    --help                                               Show this message    │
│                                                         and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: schemagin visualize [OPTIONS] SCHEMA                                    
                                                                                
 Render schema diagrams in various formats and optionally export the schema     
 concurrently.                                                                  
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    schema      TEXT  Path to schema file, '-' for stdin, or agilink:// URI │
│                        [default: None]                                       │
│                        [required]                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --format                        TEXT  Concurrently export the schema in the  │
│                                       specified format.                      │
│ --visual                        TEXT  Generate visualizations in specified   │
│                                       formats. Can be specified multiple     │
│                                       times.                                 │
│                                       [default: d2]                          │
│ --ascii         --no-ascii            Display ASCII visualization of the     │
│                                       schema.                                │
│                                       [default: no-ascii]                    │
│ --output-dir                    TEXT  Output directory path. Defaults to     │
│                                       outputs/schemagin/                     │
│                                       [default: outputs/schemagin]           │
│ --verbose       --no-verbose          Show additional debug information.     │
│                                       [default: no-verbose]                  │
│ --quiet         --no-quiet            Suppress all output except critical    │
│                                       errors.                                │
│                                       [default: no-quiet]                    │
│ --help                                Show this message and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: datagin ingest [OPTIONS] PROMPT INPUT                                   
                                                                                
 Extract and structure data from an input source.                               
 Examples:                                                                      
 datagin ingest "Extract user names and emails" input.txt --output-agilink      
 "sqlite:///output.db"                                                          
 datagin ingest "Parse invoice details" report.pdf --output-agilink             
 "duckdb:///invoices.db"                                                        
 cat data.json | datagin ingest "Structure this JSON data" - --output-agilink   
 "postgresql://user:pass@host/db"                                               
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT  Natural language description of the data extraction   │
│                        task                                                  │
│                        [default: None]                                       │
│                        [required]                                            │
│ *    input       TEXT  Input source (text, file, or agilink URI)             │
│                        [default: None]                                       │
│                        [required]                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --output-agilink                    TEXT     Agilink URI where structured    │
│                                              data will be written            │
│                                              [default: defaultdir]           │
│ --output-dir                        TEXT     Base directory for output files │
│                                              [default: ./outputs/datagin]    │
│ --intelligence                      INTEGER  Intelligence level (0-100).     │
│                                              0-33: Super fast small, 34-66:  │
│                                              Super fast big, 67-100:         │
│                                              Thinking mode                   │
│                                              [default: 50]                   │
│ --rows                              INTEGER  Number of rows to transfer if   │
│                                              input is a large dataset        │
│ --verbose           --no-verbose             Show detailed processing output │
│                                              [default: no-verbose]           │
│ --help                                       Show this message and exit.     │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: datagin synthesize [OPTIONS] PROMPT SCHEMA                              
                                                                                
 Generate synthetic data based on schema and prompt.                            
 Examples:                                                                      
 datagin synthesize "Generate 100 realistic customer records" schema.yaml       
 --output-agilink "sqlite:///customers.db" --rows 100                           
 datagin synthesize "Create 5 test orders" "agilink://path/to/schema"           
 --output-agilink "duckdb:///orders.db" -r 5                                    
 echo 'tables: users: columns: id: INTEGER name: TEXT' | datagin synthesize     
 "Make 2 users" - --output-agilink "sqlite:///:memory:" -r 2                    
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT  Natural language description of data to generate      │
│                        [default: None]                                       │
│                        [required]                                            │
│ *    schema      TEXT  Schema file path, inline YAML/JSON, or agilink URI    │
│                        [default: None]                                       │
│                        [required]                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --output-agilink                    TEXT     Agilink URI where generated     │
│                                              data will be stored             │
│                                              [default: defaultdir]           │
│ --output-dir                        TEXT     Base directory for output files │
│                                              [default: ./outputs/datagin]    │
│ --intelligence                      INTEGER  Intelligence level (0-100).     │
│                                              0-33: Super fast small, 34-66:  │
│                                              Super fast big, 67-100:         │
│                                              Thinking mode                   │
│                                              [default: 50]                   │
│ --rows                              INTEGER  Number of rows to generate      │
│                                              [default: 10]                   │
│ --verbose           --no-verbose             Show detailed processing output │
│                                              [default: no-verbose]           │
│ --help                                       Show this message and exit.     │
╰──────────────────────────────────────────────────────────────────────────────╯

                                                                                
 Usage: datagin transform [OPTIONS] PROMPT INPUT OUTPUT_AGILINK                 
                                                                                
 Transform structured data between schemas.                                     
 Examples:                                                                      
 datagin transform "Convert user data to new schema format" input_users.csv     
 "sqlite:///output.db"                                                          
 datagin transform "Merge product catalogs, standardizing categories"           
 ./product_data/ "duckdb:///merged_catalog.db"                                  
 export DATABASE_CONNECTION_STRING="postgresql://user:pass@host/db"             
 datagin transform "Anonymize customer PII fields" source_table "target_db_uri" 
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    prompt              TEXT  Natural language description of the           │
│                                transformation                                │
│                                [default: None]                               │
│                                [required]                                    │
│ *    input               TEXT  Input source (structured file or directory)   │
│                                [default: None]                               │
│                                [required]                                    │
│ *    output_agilink      TEXT  Agilink URI where transformed data will be    │
│                                stored                                        │
│                                [default: None]                               │
│                                [required]                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --verbose    --no-verbose      Show detailed processing output               │
│                                [default: no-verbose]                         │
│ --help                         Show this message and exit.                   │
╰──────────────────────────────────────────────────────────────────────────────╯

