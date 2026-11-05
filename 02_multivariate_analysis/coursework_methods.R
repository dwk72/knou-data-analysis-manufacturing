# KNOU multivariate coursework: privacy-safe reconstruction of methods documented
# in the submitted assignment. The original exercise CSV files were not supplied
# with the published GitHub repository. Do not claim reproduced coursework metrics.
# Usage: Rscript coursework_methods.R /path/to/exercise_csv_directory
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1) stop("Specify the folder containing the original course exercise CSV files.")
input_dir <- args[[1]]
load_exercise <- function(filename) {
  path <- file.path(input_dir, filename)
  if (!file.exists(path)) stop(sprintf("Missing exercise dataset: %s", filename))
  read.csv(path, check.names = TRUE)
}

# Assignment 1: six survey scores, histograms, scatter matrix, correlation.
survey <- load_exercise("ex1-1.csv")
stopifnot(ncol(survey) >= 7)
scores <- survey[, 2:7]
stopifnot(all(vapply(scores, is.numeric, logical(1))))
for (column in names(scores)) hist(scores[[column]], main = column, xlab = column)
pairs(scores)
print(round(cor(scores, use = "complete.obs"), 3))

# Assignment 2: PCA and biplot. The first field is treated as an identifier.
deug <- load_exercise("deug.csv")
stopifnot(ncol(deug) >= 3)
deug_numeric <- deug[, -1, drop = FALSE]
stopifnot(all(vapply(deug_numeric, is.numeric, logical(1))))
pca <- prcomp(na.omit(deug_numeric), scale. = TRUE)
print(summary(pca))
screeplot(pca, type = "lines", main = "PCA scree plot")
biplot(pca)

# Assignment 3: maximum-likelihood factor analysis with rotations.
# Uses the historical worksheet's file spelling; rename locally if needed.
favorites <- load_exercise("favoritesujects.csv")
stopifnot(ncol(favorites) >= 4)
favorites_numeric <- favorites[, -1, drop = FALSE]
stopifnot(all(vapply(favorites_numeric, is.numeric, logical(1))))
favorites_numeric <- na.omit(favorites_numeric)
for (rotation in c("none", "varimax", "promax")) {
  fit <- factanal(favorites_numeric, factors = 2, rotation = rotation)
  cat("\nRotation:", rotation, "\n")
  print(fit$loadings)
}
