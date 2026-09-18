# Academic foundation: monthly industrial production index time-series analysis
# Cleaned portfolio version. Replace input paths with your own local files.

library(readxl)
library(zoo)
library(ggplot2)
library(forecast)
library(magrittr)
library(tseries)

# Input files used in coursework
raw_df <- read_excel("data/Original Series.xlsx", sheet = "데이터")
sa_df  <- read_excel("data/Seasonally Adjusted.xlsx", sheet = "데이터")

raw_row <- raw_df[1, ]
sa_row  <- sa_df[1, ]

raw_val <- as.numeric(raw_row[1, -1])
sa_val  <- as.numeric(sa_row[1, -1])

date_m <- seq(
  as.Date("2000-01-01"),
  as.Date("2025-12-01"),
  by = "month"
)

prod_zoo <- zoo(
  cbind(
    original = raw_val,
    seasonally_adjusted = sa_val
  ),
  date_m
)

# Spectrum
spec_raw <- spectrum(
  coredata(prod_zoo[, "original"]),
  spans = c(3, 3),
  plot = FALSE
)

spec_sa <- spectrum(
  coredata(prod_zoo[, "seasonally_adjusted"]),
  spans = c(3, 3),
  plot = FALSE
)

plot(
  spec_raw$freq,
  spec_raw$spec,
  type = "l",
  xlab = "Frequency",
  ylab = "Spectrum",
  main = "Original vs Seasonally Adjusted Spectrum"
)
lines(spec_sa$freq, spec_sa$spec)

# Log transform and differencing
sa_zoo <- prod_zoo[, "seasonally_adjusted"]
log_sa <- log(sa_zoo)
diff_log_sa <- diff(log_sa)

# ADF tests
print(adf.test(log_sa))
print(adf.test(diff_log_sa))

# ACF / PACF using ggtsdisplay
log_sa_ts <- ts(
  coredata(log_sa),
  start = c(2000, 1),
  frequency = 12
)

diff_log_sa_ts <- ts(
  coredata(diff_log_sa),
  start = c(2000, 2),
  frequency = 12
)

ggtsdisplay(
  log_sa_ts,
  main = "Log Seasonally Adjusted Series",
  theme = theme_bw()
)

ggtsdisplay(
  diff_log_sa_ts,
  main = "Differenced Log Seasonally Adjusted Series",
  theme = theme_bw()
)
