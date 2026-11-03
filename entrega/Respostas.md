# Atividade: Reconhecimento de Gestos com Deep Learning
## Respostas 

### 1. Esse modelo é um deep learning ou um machine learning?
O modelo é um **deep learning**. Ele utiliza a arquitetura MobileNetV2, que é uma Rede Neural Convolucional (CNN - Convolutional Neural Network) profunda, com múltiplas camadas escondidas. O uso de uma rede neural profunda com transfer learning para extrair features complexas de imagens (bordas, texturas, formas) a classifica na subárea de deep learning dentro de machine learning.

### 2. Que características da imagem o modelo usa para distinguir os gestos?
O modelo usa padrões visuais como contornos da mão, número de dedos levantados, textura da pele e forma geral da mão dentro da região recortada (ROI). 
**Experimento para testar a hipótese:** Usar uma luva colorida (ex: luva de borracha verde) ao fazer os sinais, ou desenhar linhas pretas na mão. 
**O que foi observado:** O modelo, treinado apenas com mãos nuas, terá dificuldade ou errará completamente a classificação com a luva. Isso mostra que ele aprendeu não apenas o contorno e a forma matemática do gesto, mas também dependia fortemente da cor, textura da pele e iluminação do conjunto de treinamento original.

### 3. Que decisões na coleta de dados ajudam ou prejudicam o modelo?
* **Ajudam:** Intercalar fundos diferentes e iluminações durante a coleta (em vez de gravar tudo num cenário só e depois no outro). Isso previne que o modelo associe o cenário ao invés do sinal da mão e garante que o conjunto de validação, que pega os últimos 20% das imagens de cada classe (conforme o código de `train.py`), tenha diversidade representativa. Variar as mãos (esquerda e direita) e a distância da câmera também ajuda a criar um modelo mais robusto.
* **Prejudicam:** Gravar as imagens com a mão exatamente na mesma posição estática, sem variar a distância ou ângulo. Isso faz com que o modelo decore os pixels exatos daquela posição (overfitting), resultando em alta acurácia no treinamento e validação (se houver vazamento de dados), mas péssimo desempenho no mundo real (como no script `play.py`) quando a mão é posicionada levemente diferente.

### 4. Teste: como o modelo se comporta se você treinar com dados que têm pessoas no fundo?
**O que aconteceu com as previsões:** Quando testamos o modelo em um ambiente onde há outras pessoas ou rostos no fundo da imagem, as previsões ficam erráticas e a confiança oscila muito, frequentemente classificando mãos como sinais incorretos ou não reconhecendo a mão adequadamente.
**Por que o modelo teve esse comportamento:** A base do MobileNetV2 foi pré-treinada no ImageNet (que tem muitas fotos de pessoas e rostos). Como congelamos a base, o modelo ainda sabe reconhecer rostos e formas humanas. Se os dados de treino não continham pessoas no fundo, a camada densa final não aprendeu a ignorar rostos. Então, ao ver um rosto no fundo durante o teste, características fortes chamam a atenção da rede e confundem a ativação da "cabeça" que foi treinada apenas com fundos neutros.
**Duas estratégias para melhorar:**
1. **Adicionar imagens com pessoas no fundo no dataset de treinamento:** Ao coletar os sinais de libras para a classe "nada" e para os próprios sinais, pedir para outras pessoas caminharem ao fundo. Isso forçará a rede a aprender que rostos ao fundo são ruído e não o sinal alvo.
2. **Segmentação da Mão (MediaPipe):** Usar uma biblioteca como o MediaPipe Hands para primeiro detectar e recortar apenas o contorno exato da mão, ou mascarar/borrar tudo que não for a mão, antes de passar a imagem para a CNN. Isso retira completamente a influência do fundo.