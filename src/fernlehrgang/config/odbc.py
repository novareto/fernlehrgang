from ibm_db_sa import reflection as ibm_reflection
from ibm_db_sa.base import DB2Compiler 
from ibm_db_sa.pyodbc import AS400Dialect_pyodbc, DB2ExecutionContext_pyodbc
from sqlalchemy.engine import default
from sqlalchemy.connectors.mxodbc import MxODBCConnector

class MyDB2Compiler(DB2Compiler):

    def visit_sequence(self, sequence):
        import pdb; pdb.set_trace()
        nn = sequence.name
        if sequence.metadata.schema:
            nn = "%s.%s" %(sequence.metadata.schema, nn)
        return "NEXT VALUE FOR %s" % nn


#class AS400Dialect_pyodbc(MxODBCConnector, AS400Dialect_pyodbc):
class AS400Dialect_pyodbc(AS400Dialect_pyodbc):

    _reflector_cls = ibm_reflection.AS400Reflector
    execution_ctx_cls = DB2ExecutionContext_pyodbc
    statement_compiler = DB2Compiler

    def initialize(self, connection):
        super(default.DefaultDialect, self).initialize(connection)
        try:
            self.dbms_ver = connection.connection.dbms_ver
            self.dbms_name = connection.connection.dbms_name
        except:
            self.dbms_ver = ""
            self.dbms_name = ""
