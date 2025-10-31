import { publicProcedure, router } from "../_core/trpc";
import { z } from "zod";
import { loadModel, predict } from "../_core/model";

// Carregar o modelo e as métricas na inicialização do servidor
const { model, vectorizer, metrics } = loadModel();

export const smishingRouter = router({
  predict: publicProcedure
    .input(
      z.object({
        message: z.string().min(1),
        modelName: z.enum(["Random Forest", "Naive Bayes"]).default("Random Forest"),
      })
    )
    .mutation(({ input }) => {
      const { message, modelName } = input;
      
      // A previsão é feita com base no modelo e vetorizador carregados
      const prediction = predict(message, modelName, model, vectorizer);

      // Buscar as métricas do modelo selecionado, garantindo que o F1-Score seja o padrão
      const modelMetrics = metrics[modelName];
      const f1Score = modelMetrics["F1-Score"];

      // O modelo de IA é selecionado com base no F1-Score para ser a métrica padrão
      const recommendedModel = Object.keys(metrics).reduce((a, b) => 
        metrics[a]["F1-Score"] > metrics[b]["F1-Score"] ? a : b
      );

      return {
        prediction,
        f1Score,
        recommendedModel,
      };
    }),
});
