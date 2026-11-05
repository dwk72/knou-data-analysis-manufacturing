# Reconstructed from the user's KNOU regression coursework DOCX.
# Base R mtcars data; does not expose original DOCX or personal details.
# This consolidates the documented steps, not a byte-for-byte original script.

data(mtcars)
predictors <- setdiff(names(mtcars), "mpg")

# Step 1: single-variable models; compare fit and significance.
single <- do.call(rbind, lapply(predictors, function(v) {
  fit <- lm(reformulate(v, response = "mpg"), data = mtcars)
  data.frame(predictor = v,
             r_squared = summary(fit)$r.squared,
             model_p = pf(summary(fit)$fstatistic[1],
                          summary(fit)$fstatistic[2],
                          summary(fit)$fstatistic[3], lower.tail = FALSE))
}))
print(single[order(-single$r_squared), ], row.names = FALSE)

# Step 2: compare each predictor added to the weight baseline.
base <- lm(mpg ~ wt, data = mtcars)
added <- do.call(rbind, lapply(setdiff(predictors, "wt"), function(v) {
  fit <- lm(reformulate(c("wt", v), response = "mpg"), data = mtcars)
  change <- anova(base, fit)
  data.frame(added_predictor = v,
             extra_sum_squares = change$`Sum of Sq`[2],
             p_value = change$`Pr(>F)`[2])
}))
print(added[order(-added$extra_sum_squares), ], row.names = FALSE)

# Step 3: wt+cyl model and standardized predictors.
fit_two <- lm(mpg ~ wt + cyl, data = mtcars)
print(summary(fit_two))
standardized <- as.data.frame(scale(mtcars[c("mpg", "wt", "cyl")]))
fit_std <- lm(mpg ~ wt + cyl, data = standardized)
cat("\nStandardized coefficients:\n")
print(coef(fit_std))
