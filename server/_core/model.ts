import { performance } from "perf_hooks";
import { execSync } from "child_process";
import * as path from "path";

// Tipos básicos para o resultado da previsão
type PredictionResult = {
  label: "phishing" | "nao-phishing";
  probability: number;
};

// Métrica de exemplo para simular o F1-Score e a acurácia
// ATENÇÃO: Estes valores são simulados. Você DEVE substituí-los pelas métricas reais do seu modelo.
const realMetrics = {
  "Random Forest": {
    "Accuracy": 0.9786,
    "F1-Score": 0.9250, // Substitua pelo F1-Score real do seu Random Forest
    "Precision": 0.9800,
    "Recall": 0.8750,
  },
  "Naive Bayes": {
    "Accuracy": 0.9600,
    "F1-Score": 0.8800, // Substitua pelo F1-Score real do seu Naive Bayes
    "Precision": 0.9500,
    "Recall": 0.8200,
  },
};

// Caminho para o script Python de previsão
const PREDICT_SCRIPT_PATH = path.join(process.cwd(), "backend", "predict.py");

/**
 * Carrega as métricas do modelo.
 * Não carrega o modelo em si, pois a previsão será feita chamando o script Python.
 */
export function loadModel(): { metrics: typeof realMetrics } {
  console.log("Carregando métricas do modelo...");
  // A lógica de carregamento real do modelo está no script Python.
  return { metrics: realMetrics };
}

/**
 * Realiza a previsão chamando o script Python.
 * @param message A mensagem de texto a ser analisada.
 * @param modelName O nome do modelo a ser usado.
 * @returns Um objeto com o resultado da previsão (phishing ou não) e a probabilidade.
 */
export function predict(message: string, modelName: "Random Forest" | "Naive Bayes"): PredictionResult {
  const startTime = performance.now();
  console.log(`Previsão usando ${modelName} para a mensagem: "${message}"`);

  try {
    // 1. Escapa a mensagem para ser passada como argumento de linha de comando
    const escapedMessage = message.replace(/"/g, '\\"');
    
    // 2. Define o caminho para o executável Python dentro do seu ambiente virtual (venv)
    // Assumindo ambiente Linux/Mac, que é o padrão do sandbox.
    const pythonExecutable = path.join(process.cwd(), "venv", "bin", "python");
    
    // 3. Comando completo para executar o script Python
    // Formato: <caminho_python> <caminho_script> "<mensagem>" "<nome_modelo>"
    const command = `${pythonExecutable} ${PREDICT_SCRIPT_PATH} "${escapedMessage}" "${modelName}"`;

    // 4. Executa o comando de forma síncrona
    // O maxBuffer é aumentado para garantir que a saída do script Python não seja truncada
    const stdout = execSync(command, { encoding: 'utf8', maxBuffer: 1024 * 1024 });

    // 5. O script Python retorna um JSON no stdout
    const result = JSON.parse(stdout.trim());
    
    if (result.error) {
      // Se o script Python retornar um erro (ex: modelo não encontrado), lança exceção
      throw new Error(`Erro no script Python: ${result.error}`);
    }
    
    const endTime = performance.now();
    console.log(`Previsão concluída em ${(endTime - startTime).toFixed(2)}ms. Resultado: ${result.label}`);

    return {
      label: result.label,
      probability: result.probability,
    };
  } catch (error) {
    console.error("Erro ao executar script Python de previsão:", error);
    // Em caso de erro, retorna um resultado padrão de "não-phishing" para evitar quebrar a aplicação.
    return {
      label: "nao-phishing",
      probability: 0.0,
    };
  }
}
