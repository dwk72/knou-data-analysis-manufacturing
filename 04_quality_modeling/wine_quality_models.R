# Academic foundation: wine-quality regression/classification
# Data file is not included in this repository.

wine <- read.csv("data/winequalityCLASS.csv", header = TRUE)

# 1) Linear regression
fit_lm_all <- lm(quality ~ ., data = wine)
fit_lm_step <- step(fit_lm_all, direction = "both")

pred_reg <- predict(
  fit_lm_step,
  newdata = wine,
  type = "response"
)

# Metrics recorded in the coursework:
# MSE = 0.173835
# MAE = 0.358183

# 2) Logistic regression
fit_glm_all <- glm(
  quality ~ .,
  family = binomial,
  data = wine
)

fit_glm_step <- step(
  fit_glm_all,
  direction = "both"
)

p <- predict(
  fit_glm_step,
  newdata = wine,
  type = "response"
)

cutoff <- 0.5
yhat <- ifelse(p > cutoff, 1, 0)

confusion <- table(
  wine$quality,
  yhat,
  dnn = c("Observed", "Predicted")
)

print(confusion)

# Coursework result:
# Accuracy    = 75.1%
# Sensitivity = 76.7%
# Specificity = 73.2%
