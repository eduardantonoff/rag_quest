if not exist "data\db" mkdir data\db
if not exist "data\db\neo4j" mkdir data\db\neo4j
if not exist "data\db\neo4j\data" mkdir data\db\neo4j\data
if not exist "data\db\neo4j\logs" mkdir data\db\neo4j\logs
if not exist "data\db\neo4j\plugins" mkdir data\db\neo4j\plugins
if not exist "data\db\neo4j\licenses" mkdir data\db\neo4j\licenses
if not exist "data\db\neo4j\plugins" mkdir data\db\neo4j\plugins


docker run --restart always -p 7474:7474 -p 7687:7687 -v ".\data\db\neo4j\data:/data" -v ".\data\db\neo4j\logs:/logs" -v ".\data\db\neo4j\plugins:/plugins" -v ".\data\db\neo4j\licenses:/licenses" -e NEO4J_AUTH=none -e NEO4J_PLUGINS="[\"apoc\", \"graph-data-science\"]" neo4j:5.18