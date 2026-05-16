import os
import logging
from llm.core.types import LLMInput, Message, Role, ToolDefinition
from llm.providers import get_provider
from llm.dispatcher import Dispatcher
from llm.session_recorder import SessionRecorder

def run_live_validation():
    print("Iniciando fluxo operacional real (Gemini API)...")
    
    # 1. Configuração
    session_id = "live-prod-validation-001"
    recorder = SessionRecorder(session_id=session_id)
    provider = get_provider("gemini", api_key=os.environ.get("GEMINI_API_KEY"))
    dispatcher = Dispatcher(hook_path="scripts/hooks/quality-gate.js", recorder=recorder)
    
    # 2. Definição da Ferramenta
    bash_tool = ToolDefinition(
        name="bash",
        description="Executa comandos shell",
        parameters={"type": "object", "properties": {"command": {"type": "string"}}}
    )
    
    # 3. Request Real
    input_data = LLMInput(
        messages=[Message(role=Role.USER, content="Liste os arquivos do diretório atual usando bash.")],
        tools=[bash_tool],
        session_id=session_id
    )
    
    try:
        # Inferência
        output = provider.generate(input_data)
        
        if output.tool_calls:
            print(f"ToolCall detectada: {output.tool_calls[0].name}")
            # Governança
            mutated = dispatcher.dispatch(output.tool_calls[0], session_id=session_id)
            if mutated:
                print(f"Sucesso: Ferramenta validada. Args: {mutated.arguments}")
            else:
                print("Veto: Execução bloqueada pela governança.")
        else:
            print(f"Resposta direta: {output.content}")
            
    except Exception as e:
        print(f"Incidente de Runtime: {e}")

if __name__ == "__main__":
    run_live_validation()
