# Set working directory to Music Research folder on Desktop
setwd("~/Desktop/Music Research")

# Load libraries
library(janitor)
library(tidyverse)

# Define file paths (now relative to the working directory)
control_file <- "audio_metrics_control.csv"
treatment_file <- "audio_metrics_treatment.csv"

# Define output directory for plots
output_dir <- "distribution_images"
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

# Read and clean CSV files
control_df <- read_csv(control_file) %>% clean_names()
treatment_df <- read_csv(treatment_file) %>% clean_names()

# Add dataset labels
control_df$Dataset <- "Control"
treatment_df$Dataset <- "Treatment"

# Equalize sample sizes
min_size <- min(nrow(control_df), nrow(treatment_df))
set.seed(42)
control_sample <- sample_n(control_df, min_size)
treatment_sample <- sample_n(treatment_df, min_size)
balanced_df <- bind_rows(control_sample, treatment_sample)

# Identify numeric columns
numerical_columns <- balanced_df %>% select(where(is.numeric)) %>% colnames()

# Color scheme
control_color <- "#1f77b4"
treatment_color <- "#d62728"

# Aesthetic theme
custom_theme <- theme_minimal(base_size = 14) +
  theme(
    legend.position = "top",
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.title = element_text(face = "bold"),
    axis.text = element_text(size = 12),
    legend.text = element_text(size = 12),
    legend.title = element_blank()
  )

# Generate plots
for (col in numerical_columns) {
  # 1️⃣ Overlapping Density Plot
  p1 <- ggplot(balanced_df, aes(x = .data[[col]], fill = Dataset)) +
    geom_density(alpha = 0.4, color = "black", linewidth = 1) +
    scale_fill_manual(values = c("Control" = control_color, "Treatment" = treatment_color)) +
    labs(title = paste("Distribution of", col), x = col, y = "Density") +
    custom_theme
  
  ggsave(filename = file.path(output_dir, paste0(col, "_overlapping_density.png")), plot = p1, width = 8, height = 5, dpi = 300)
  
  # 2️⃣ Faceted Density Plot
  p2 <- ggplot(balanced_df, aes(x = .data[[col]])) +
    geom_density(fill = control_color, alpha = 0.5, linewidth = 1) +
    facet_wrap(~Dataset, scales = "free") +
    labs(title = paste("Distribution of", col), x = col, y = "Density") +
    custom_theme
  
  ggsave(filename = file.path(output_dir, paste0(col, "_facet_density.png")), plot = p2, width = 8, height = 5, dpi = 300)
  
  # 3️⃣ Line Density Plot (Just Outlines)
  p3 <- ggplot(balanced_df, aes(x = .data[[col]], color = Dataset)) +
    geom_density(size = 1.5) +
    scale_color_manual(values = c("Control" = control_color, "Treatment" = treatment_color)) +
    labs(title = paste("Distribution of", col), x = col, y = "Density") +
    custom_theme
  
  ggsave(filename = file.path(output_dir, paste0(col, "_line_density.png")), plot = p3, width = 8, height = 5, dpi = 300)
}

# Report tempo means
cat("Mean Tempo (BPM) — Control:", mean(control_sample$tempo_bpm, na.rm = TRUE), "\n")
cat("Mean Tempo (BPM) — Treatment:", mean(treatment_sample$tempo_bpm, na.rm = TRUE), "\n")
