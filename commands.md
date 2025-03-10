                                                                             
 Usage: dagify [OPTIONS] COMMAND [ARGS]...                                   
                                                                             
 DAG generation and compilation tool                                         
                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                               │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────╮
│ compose   Creates a new workflow from a description, supporting different │
│           types of workflow representations.                              │
│ refine    Refines an existing workflow by improving metadata, details,    │
│           instructions and tags. Can also apply agent tags to enable      │
│           agentic execution of workflow steps.                            │
│ resolve   Executes one pass of AI-assisted refinement to replace          │
│           agent-tagged workflow steps with progressively more concrete    │
│           instructions and generated code, while respecting a defined     │
│           type hierarchy.                                                 │
│ compile   Compiles a DAG into an executable format by fully implementing  │
│           functions where possible, resolving AI-shims, and generating    │
│           structured output files.                                        │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagify compose [OPTIONS] PROMPT [DATA]                               
                                                                             
 Creates a new workflow from a description, supporting different types of    
 workflow representations.                                                   
 Examples:     1. Create a new DAG from a description:        $ dagify       
 compose "Extract data from API, transform, and load to database"            
 2. Create a DAG using an existing workflow as reference:        $ dagify    
 compose "Create CI pipeline" reference_workflow.json                        
 3. Create a DAG using piped input as reference:        $ cat                
 reference_workflow.json | dagify compose "Optimize this workflow" -         
 4. Create a DAG from a database schema:        $ dagify compose "Generate   
 ETL pipeline" "postgres://user:pass@localhost:5432/db"                      
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT    Description of the process or workflow to        │
│                          generate a DAG for                               │
│                          [default: None]                                  │
│                          [required]                                       │
│      data        [DATA]  DAG source - can be a JSON file, agilink URI,    │
│                          JSON string, or database connection. Use '-' for │
│                          stdin                                            │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --type                  [plain|typed|spec|code-  Type of DAG to generate  │
│                         ai-shim|code]            (plain, typed, spec,     │
│                                                  code-ai-shim, code)      │
│                                                  [default: plain]         │
│ --intelligence          INTEGER RANGE            Intelligence level       │
│                         [0<=x<=100]              (0-100) for AI-assisted  │
│                                                  DAG generation           │
│                                                  [default: 50]            │
│ --seed                  INTEGER                  Seed for deterministic   │
│                                                  workflow generation      │
│                                                  [default: None]          │
│ --output-dir            TEXT                     Directory to save the    │
│                                                  generated DAG and        │
│                                                  visualization            │
│                                                  [default: ./dagify/]     │
│ --viz-format            TEXT                     Format for DAG           │
│                                                  visualization (dot,      │
│                                                  yaml, json, dbml, d2)    │
│                                                  [default: d2]            │
│ --no-display                                     Suppress ASCII           │
│                                                  visualization of the     │
│                                                  generated DAG            │
│ --verbose                                        Enable verbose output    │
│ --version       -v                               Show version and exit    │
│ --help                                           Show this message and    │
│                                                  exit.                    │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagify refine [OPTIONS] PROMPT [DATA]                                
                                                                             
 Refines an existing workflow by improving metadata, details, instructions   
 and tags. Can also apply agent tags to enable agentic execution of workflow 
 steps.                                                                      
 Examples:     1. Refine a DAG by improving metadata and relationships:      
 $ dagify refine "Enhance step dependencies" agilink://ci_pipeline           
 2. Apply agent tags to enable AI execution in an ETL DAG:        $ dagify   
 refine "Make AI-driven transformations agentic" etl_dag.json --agentify     
 3. Use piped input for DAG refinement:        $ cat workflow_dag.json |     
 dagify refine "Optimize parallel execution" -                               
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT    Description of the refinement to be applied      │
│                          [default: None]                                  │
│                          [required]                                       │
│      data        [DATA]  DAG source - can be a JSON file, agilink URI, or │
│                          JSON string. Use '-' for stdin                   │
│                          [default: None]                                  │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --intelligence        INTEGER RANGE             Intelligence level        │
│                       [0<=x<=100]               (0-100) for AI-assisted   │
│                                                 DAG generation            │
│                                                 [default: 50]             │
│ --seed                INTEGER                   Seed for deterministic    │
│                                                 workflow generation       │
│                                                 [default: None]           │
│ --agentify                                      Apply agent tags to       │
│                                                 enable agentic execution  │
│                                                 of applicable workflow    │
│                                                 steps                     │
│ --viz-format          TEXT                      Format of the DAG output  │
│                                                 (dot, yaml, json, dbml,   │
│                                                 d2)                       │
│                                                 [default: d2]             │
│ --output-dir          TEXT                      Directory to save the     │
│                                                 refined DAG and viz       │
│                                                 [default: ./dagify/]      │
│ --no-display                                    Suppress ASCII            │
│                                                 visualization of the      │
│                                                 generated DAG             │
│ --verbose                                       Enable verbose output     │
│ --help                                          Show this message and     │
│                                                 exit.                     │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagify resolve [OPTIONS] PROMPT DATA                                 
                                                                             
 Executes one pass of AI-assisted refinement to replace agent-tagged         
 workflow steps with progressively more concrete instructions and generated  
 code, while respecting a defined type hierarchy.                            
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT  Description of how to resolve agent tags           │
│                        [default: None]                                    │
│                        [required]                                         │
│ *    data        TEXT  The DAG to resolve (file path, JSON string, or     │
│                        agilink URI)                                       │
│                        [default: None]                                    │
│                        [required]                                         │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --type-floor          [plain|typed|spec|code-a  The minimum DAG type to   │
│                       i-shim|code]              resolve down to           │
│                                                 [default: spec]           │
│ --intelligence        INTEGER RANGE             Intelligence level        │
│                       [0<=x<=100]               (0-100) for AI-assisted   │
│                                                 DAG generation            │
│                                                 [default: 50]             │
│ --seed                INTEGER                   Seed for deterministic    │
│                                                 workflow generation       │
│                                                 [default: None]           │
│ --viz-format          TEXT                      Format of the DAG output  │
│                                                 (dot, yaml, json, dbml,   │
│                                                 d2)                       │
│                                                 [default: d2]             │
│ --output-dir          TEXT                      Directory to save the     │
│                                                 refined DAG and viz       │
│                                                 [default: ./dagify/]      │
│ --no-display                                    Suppress ASCII            │
│                                                 visualization of the      │
│                                                 generated DAG             │
│ --verbose                                       Enable verbose output     │
│ --help                                          Show this message and     │
│                                                 exit.                     │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagify compile [OPTIONS] [PROMPT] [DATA]                             
                                                                             
 Compiles a DAG into an executable format by fully implementing functions    
 where possible, resolving AI-shims, and generating structured output files. 
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│   prompt      [PROMPT]  Description of how to compile the DAG             │
│   data        [DATA]    The DAG to compile (file path, JSON string, or    │
│                         agilink URI)                                      │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --type-floor             [plain|typed|spec|code  The minimum DAG type to  │
│                          -ai-shim|code]          compile down to          │
│                                                  [default: code]          │
│ --intelligence           INTEGER RANGE           Intelligence level       │
│                          [0<=x<=100]             (0-100) for AI-assisted  │
│                                                  function generation      │
│                                                  [default: 50]            │
│ --seed                   INTEGER                 Seed for deterministic   │
│                                                  DAG compilation          │
│                                                  [default: None]          │
│ --output-format  -f      [json|yaml|python|bash  Format for the compiled  │
│                          |docker-compose]        DAG                      │
│                                                  [default: python]        │
│ --output-dir             TEXT                    Directory to save the    │
│                                                  compiled DAG and         │
│                                                  artifacts                │
│                                                  [default:                │
│                                                  ./dagify/compiled/]      │
│ --no-display                                     Suppress ASCII           │
│                                                  visualization of the     │
│                                                  compiled DAG             │
│ --verbose                                        Enable verbose output    │
│ --help                                           Show this message and    │
│                                                  exit.                    │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagent [OPTIONS] COMMAND [ARGS]...                                   
                                                                             
 DAG execution, optimization, and synthesis tool                             
                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                               │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────╮
│ validate     Validates the correctness of a DAG by checking its           │
│              structure, dependencies, and execution feasibility.          │
│ optimize     Optimizes AI-driven DAG nodes (e.g., prompts, spec stages)   │
│              to improve accuracy and reliability by tuning them against a │
│              provided test dataset.                                       │
│ execute      Execute a DAG plan with structured input and AI-assisted     │
│              processing.                                                  │
│ interpret    Generates a DAG plan dynamically and executes it             │
│              immediately.                                                 │
│ synthesize   Generates a DAG plan, compiles it to executable code, and    │
│              executes it.                                                 │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagent validate [OPTIONS] PLAN                                       
                                                                             
 Validates the correctness of a DAG by checking its structure, dependencies, 
 and execution feasibility.                                                  
 Performs validation checks including: - DAG structural integrity (node/edge 
 consistency, cycles) - Execution compatibility (AI-executable steps,        
 missing dependencies) - Schema correctness for external data sources        
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    plan      TEXT  The DAG plan to validate. Can be a DAGify JSON file, │
│                      agilink URI, or DAG JSON string (stdin)              │
│                      [required]                                           │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --strict           Enable strict validation (fail on warnings)            │
│ --verbose          Enable verbose output                                  │
│ --help             Show this message and exit.                            │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagent optimize [OPTIONS] PLAN TEST_DATA                             
                                                                             
 Optimizes AI-driven DAG nodes (e.g., prompts, spec stages) to improve       
 accuracy and reliability by tuning them against a provided test dataset.    
 Optimization can adjust: - Prompt structure - Spec-level AI-generated       
 values - Other AI-dependent nodes in the DAG                                
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    plan           TEXT  The DAG plan to optimize. Can be a DAGify JSON  │
│                           file, agilink URI, or DAG JSON string (stdin)   │
│                           [required]                                      │
│ *    test_data      TEXT  The test dataset to optimize against. Can be a  │
│                           structured data file (JSON, CSV, Parquet) or    │
│                           agilink URI                                     │
│                           [required]                                      │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --metric                [accuracy|mse|custom]  Optimization metric to use │
│                                                [default: accuracy]        │
│ --max-iterations        INTEGER                Maximum optimization       │
│                                                passes                     │
│                                                [default: 10]              │
│ --output-dir            TEXT                   Directory to save          │
│                                                optimized DAG              │
│                                                [default:                  │
│                                                ./dagent/optimized/]       │
│ --verbose                                      Enable verbose output      │
│ --help                                         Show this message and      │
│                                                exit.                      │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagent execute [OPTIONS] [PLAN] [DATA]                               
                                                                             
 Execute a DAG plan with structured input and AI-assisted processing.        
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│   plan      [PLAN]  DAG plan to execute. Can be a JSON file, agilink URI, │
│                     or JSON string. Use '-' for stdin                     │
│   data      [DATA]  External data to provide during execution             │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --jit                    [prefine|dynamic|predi  Just-in-time (JIT)       │
│                          ct]                     refinement mode          │
│                                                  [default: None]          │
│ --tools                  TEXT                    Comma-separated list of  │
│                                                  CLI tools available in   │
│                                                  the runtime              │
│                                                  [default: None]          │
│ --tools-file             TEXT                    File containing a list   │
│                                                  of tools (one per line)  │
│                                                  [default: None]          │
│ --output-format  -f      [json|yaml|python|bash  Format for execution     │
│                          |docker-compose]        results                  │
│                                                  [default: json]          │
│ --output-dir             TEXT                    Directory to save        │
│                                                  execution results        │
│                                                  [default:                │
│                                                  ./dagent/outputs/]       │
│ --intelligence           INTEGER RANGE           Intelligence level       │
│                          [0<=x<=100]             (0-100) to determine     │
│                                                  model selection          │
│                                                  [default: 50]            │
│ --seed                   INTEGER                 Seed for deterministic   │
│                                                  execution                │
│                                                  [default: None]          │
│ --verbose                                        Enable verbose output    │
│ --help                                           Show this message and    │
│                                                  exit.                    │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagent interpret [OPTIONS] [TASK] [DATA]                             
                                                                             
 Generates a DAG plan dynamically and executes it immediately.               
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│   task      [TASK]  Natural language description of the DAG plan          │
│   data      [DATA]  Input dataset or connection                           │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --recursive                                    Allow recursively          │
│                                                generated DAGs             │
│ --jit               [prefine|dynamic|predict]  Just-in-time (JIT)         │
│                                                refinement mode            │
│                                                [default: None]            │
│ --tools             TEXT                       Comma-separated list of    │
│                                                CLI tools available in the │
│                                                runtime                    │
│                                                [default: None]            │
│ --tools-file        TEXT                       File containing a list of  │
│                                                tools (one per line)       │
│                                                [default: None]            │
│ --output-dir        TEXT                       Directory to save results  │
│                                                [default:                  │
│                                                ./dagent/outputs/]         │
│ --verbose                                      Enable verbose output      │
│ --help                                         Show this message and      │
│                                                exit.                      │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: dagent synthesize [OPTIONS] [TASK] [DATA]                            
                                                                             
 Generates a DAG plan, compiles it to executable code, and executes it.      
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│   task      [TASK]  Natural language description of the DAG               │
│   data      [DATA]  Input dataset or connection                           │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --recursive                                     Allow recursively         │
│                                                 generated DAGs            │
│ --jit                [prefine|dynamic|predict]  Just-in-time (JIT)        │
│                                                 refinement mode           │
│                                                 [default: None]           │
│ --tools              TEXT                       Comma-separated list of   │
│                                                 CLI tools available in    │
│                                                 the runtime               │
│                                                 [default: None]           │
│ --tools-file         TEXT                       File containing a list of │
│                                                 tools (one per line)      │
│                                                 [default: None]           │
│ --runtime-dir        TEXT                       Directory where compiled  │
│                                                 code will be stored and   │
│                                                 registered                │
│                                                 [default:                 │
│                                                 ./dagent/runtime/]        │
│ --output-dir         TEXT                       Directory to save         │
│                                                 execution results         │
│                                                 [default:                 │
│                                                 ./dagent/outputs/]        │
│ --verbose                                       Enable verbose output     │
│ --help                                          Show this message and     │
│                                                 exit.                     │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: schemagin [OPTIONS] [PROMPT] [DATA]                                  
                                                                             
 Generate a database schema using natural language.                          
 Examples:     schemagin "Schema for an e-commerce platform"     schemagin   
 "Extend this schema to support multi-tenancy" "Users table must include a   
 tenant_id column"     schemagin "Schema for a project management tool" -o   
 json     schemagin "Generate a database for an inventory system" -v dot -v  
 dbml --display-ascii     echo "Generate a database schema for a medical     
 records system" | schemagin -o sql     echo "Include an audit log table" |  
 schemagin "Schema for a financial system" -o json     schemagin "Improve    
 this schema with better indexing" < schema.yaml                             
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│   prompt      [PROMPT]  Natural language description of the schema to     │
│                         generate.                                         │
│   data        [DATA]    Optional structured schema definition or          │
│                         unstructured context. Can be provided via stdin.  │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --intelligence                           INTEGER RANGE   Intelligence     │
│                                          [0<=x<=100]     level. 0-100     │
│                                                          [default: 0]     │
│ --seed                                   INTEGER         Set a seed value │
│                                                          for              │
│                                                          deterministic    │
│                                                          schema           │
│                                                          generation.      │
│                                                          [default: None]  │
│ --output-format   -o                     [yaml|json|sql  Output format    │
│                                          |txt]           for the schema.  │
│                                                          [default: yaml]  │
│ --visualization   -v                     [dot|dbml|d2]   Generate         │
│                                                          visualizations   │
│                                                          in specified     │
│                                                          formats. Can be  │
│                                                          specified        │
│                                                          multiple times.  │
│                                                          [default: None]  │
│ --display-ascii       --no-display-a…                    Display the      │
│                                                          generated schema │
│                                                          in an ASCII      │
│                                                          table format.    │
│                                                          [default:        │
│                                                          no-display-asci… │
│ --no-foreign-ke…      --no-no-foreig…                    Disable foreign  │
│                                                          key constraints  │
│                                                          in the generated │
│                                                          schema.          │
│                                                          [default:        │
│                                                          no-no-foreign-k… │
│ --verbose             --no-verbose                       Show additional  │
│                                                          debug            │
│                                                          information.     │
│                                                          [default:        │
│                                                          no-verbose]      │
│ --help                                                   Show this        │
│                                                          message and      │
│                                                          exit.            │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: datagin [OPTIONS] COMMAND [ARGS]...                                  
                                                                             
 Converts unstructured data into structured data. Supports data transfer,    
 transformation, and synthesis using a natural language prompt.              
                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                               │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────╮
│ ingest       Extract and structure data from an input source.             │
│ synthesize   Generate synthetic data based on schema and prompt.          │
│ transform    Transform structured data between schemas.                   │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: datagin ingest [OPTIONS] PROMPT INPUT                                
                                                                             
 Extract and structure data from an input source.                            
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT  Natural language description of the data           │
│                        extraction task                                    │
│                        [default: None]                                    │
│                        [required]                                         │
│ *    input       TEXT  Input source (text, file, or agilink URI)          │
│                        [default: None]                                    │
│                        [required]                                         │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ *  --output-agilink                    TEXT     Agilink URI where         │
│                                                 structured data will be   │
│                                                 written                   │
│                                                 [env var:                 │
│                                                 DATABASE_CONNECTION_STRI… │
│                                                 [default: None]           │
│                                                 [required]                │
│    --source-agilink                    TEXT     Alias for INPUT if using  │
│                                                 an agilink URI            │
│                                                 [default: None]           │
│    --start-page                        INTEGER  Starting page for PDF     │
│                                                 processing                │
│                                                 [default: 0]              │
│    --rows                              INTEGER  Number of rows to         │
│                                                 transfer if input is a    │
│                                                 large dataset             │
│                                                 [default: None]           │
│    --verbose           --no-verbose             Show detailed processing  │
│                                                 output                    │
│                                                 [default: no-verbose]     │
│    --help                                       Show this message and     │
│                                                 exit.                     │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: datagin synthesize [OPTIONS] PROMPT SCHEMA                           
                                                                             
 Generate synthetic data based on schema and prompt.                         
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    prompt      TEXT  Natural language description of data to generate   │
│                        [default: None]                                    │
│                        [required]                                         │
│ *    schema      TEXT  Schema file path or inline YAML/JSON               │
│                        [default: None]                                    │
│                        [required]                                         │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ *  --output-agilink                    TEXT     Agilink URI where         │
│                                                 generated data will be    │
│                                                 stored                    │
│                                                 [env var:                 │
│                                                 DATABASE_CONNECTION_STRI… │
│                                                 [default: None]           │
│                                                 [required]                │
│    --rows                              INTEGER  Number of rows to         │
│                                                 generate                  │
│                                                 [default: 10]             │
│    --verbose           --no-verbose             Show detailed processing  │
│                                                 output                    │
│                                                 [default: no-verbose]     │
│    --help                                       Show this message and     │
│                                                 exit.                     │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: datagin transform [OPTIONS] PROMPT INPUT OUTPUT_AGILINK              
                                                                             
 Transform structured data between schemas.                                  
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    prompt              TEXT  Natural language description of the        │
│                                transformation                             │
│                                [default: None]                            │
│                                [required]                                 │
│ *    input               TEXT  Input source (structured file or           │
│                                directory)                                 │
│                                [default: None]                            │
│                                [required]                                 │
│ *    output_agilink      TEXT  Agilink URI where transformed data will be │
│                                stored                                     │
│                                [env var: DATABASE_CONNECTION_STRING]      │
│                                [default: None]                            │
│                                [required]                                 │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --verbose    --no-verbose      Show detailed processing output            │
│                                [default: no-verbose]                      │
│ --help                         Show this message and exit.                │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: pagint [OPTIONS] COMMAND [ARGS]...                                   
                                                                             
 Natural language-driven data generation and augmentation tool               
                                                                             
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --version  -v        Show the application's version and exit.             │
│ --help               Show this message and exit.                          │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────╮
│ generate   Generate structured data using natural language descriptions.  │
│ augment    Enhance existing data using natural language descriptions.     │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: pagint generate [OPTIONS] TASK [SCHEMA]                              
                                                                             
 Generate structured data using natural language descriptions.               
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    task        TEXT      Task description [default: None] [required]    │
│      schema      [SCHEMA]  Database connection string                     │
│                            [env var: DATABASE_CONNECTION_STRING]          │
│                            [default: None]                                │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --rows          -r      INTEGER                  Number of rows to        │
│                                                  generate                 │
│                                                  [default: 20]            │
│ --intelligence  -i      INTEGER RANGE            Intelligence level       │
│                         [0<=x<=100]              (0-100) - currently not  │
│                                                  used                     │
│                                                  [default: 50]            │
│ --no-display                                     Suppress ASCII           │
│                                                  visualization of         │
│                                                  generated data           │
│ --verbose                                        Enable verbose output    │
│ --help                                           Show this message and    │
│                                                  exit.                    │
╰───────────────────────────────────────────────────────────────────────────╯

                                                                             
 Usage: pagint augment [OPTIONS] TASK [TARGET_DB]                            
                                                                             
 Enhance existing data using natural language descriptions.                  
                                                                             
╭─ Arguments ───────────────────────────────────────────────────────────────╮
│ *    task           TEXT         Task description [default: None]         │
│                                  [required]                               │
│      target_db      [TARGET_DB]  Target database connection string        │
│                                  [env var: DATABASE_CONNECTION_STRING]    │
│                                  [default: None]                          │
╰───────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────╮
│ --intelligence  -i      INTEGER RANGE            Intelligence level       │
│                         [0<=x<=100]              (0-100) - currently not  │
│                                                  used                     │
│                                                  [default: 50]            │
│ --no-display                                     Suppress ASCII           │
│                                                  visualization of         │
│                                                  augmented data           │
│ --verbose                                        Enable verbose output    │
│ --help                                           Show this message and    │
│                                                  exit.                    │
╰───────────────────────────────────────────────────────────────────────────╯

