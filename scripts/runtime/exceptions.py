class EGCRuntimeError(Exception): pass
class ExecutionError(EGCRuntimeError): pass
class WorkflowError(EGCRuntimeError): pass
class SandboxError(EGCRuntimeError): pass
class MemoryError(EGCRuntimeError): pass
