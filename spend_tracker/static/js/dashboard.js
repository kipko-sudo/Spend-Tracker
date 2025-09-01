import { Chart } from "@/components/ui/chart"
// Dashboard Charts and Interactive Elements

// Format currency
function formatCurrency(value) {
  return "$" + Number.parseFloat(value).toFixed(2)
}

// Format percentage
function formatPercentage(value) {
  return Number.parseFloat(value).toFixed(1) + "%"
}

// Initialize charts when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Set Chart.js defaults if Chart.js is available
  if (typeof Chart !== "undefined") {
    Chart.defaults.font.family = "'Inter', sans-serif"
    Chart.defaults.font.size = 12
    Chart.defaults.color = getComputedStyle(document.documentElement).getPropertyValue("--text-light").trim()

    // Custom tooltip styling
    Chart.defaults.plugins.tooltip.backgroundColor = "rgba(0, 0, 0, 0.7)"
    Chart.defaults.plugins.tooltip.titleColor = "#fff"
    Chart.defaults.plugins.tooltip.bodyColor = "#fff"
    Chart.defaults.plugins.tooltip.padding = 10
    Chart.defaults.plugins.tooltip.cornerRadius = 6
    Chart.defaults.plugins.tooltip.displayColors = true
    Chart.defaults.plugins.tooltip.boxPadding = 6

    // Custom legend styling
    Chart.defaults.plugins.legend.labels.usePointStyle = true
    Chart.defaults.plugins.legend.labels.pointStyleWidth = 10
    Chart.defaults.plugins.legend.labels.padding = 15

    // Initialize any charts on the page
    initializeCharts()
  }

  // Initialize date pickers if available
  const datePickers = document.querySelectorAll(".date-picker")
  if (datePickers.length > 0) {
    datePickers.forEach((picker) => {
      picker.addEventListener("focus", function () {
        this.type = "date"
      })
      picker.addEventListener("blur", function () {
        if (!this.value) {
          this.type = "text"
        }
      })
    })
  }

  // Initialize dropdowns
  const dropdownTriggers = document.querySelectorAll(".dropdown-trigger")
  if (dropdownTriggers.length > 0) {
    dropdownTriggers.forEach((trigger) => {
      trigger.addEventListener("click", function (e) {
        e.preventDefault()
        e.stopPropagation()
        const dropdown = this.nextElementSibling
        dropdown.classList.toggle("open")
      })
    })

    // Close dropdowns when clicking outside
    document.addEventListener("click", () => {
      document.querySelectorAll(".dropdown.open").forEach((dropdown) => {
        dropdown.classList.remove("open")
      })
    })
  }

  // Auto-hide messages after 5 seconds
  setTimeout(() => {
    document.querySelectorAll(".message").forEach((message) => {
      message.classList.add("fade-out")
      setTimeout(() => {
        message.remove()
      }, 500)
    })
  }, 5000)
})

// Declare variables for chart data
const budgetLabels = []
const budgetData = []
const actualData = []
const expenseLabels = []
const expenseData = []
const monthLabels = []
const incomeData = []
const savingsData = []

// Initialize charts
function initializeCharts() {
  // Budget vs Actual Chart
  const budgetChartEl = document.getElementById("budgetVsActualChart")
  if (budgetChartEl) {
    const ctx = budgetChartEl.getContext("2d")
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: budgetLabels || [],
        datasets: [
          {
            label: "Budget",
            data: budgetData || [],
            backgroundColor: getComputedStyle(document.documentElement)
              .getPropertyValue("--primary-transparent")
              .trim(),
            borderColor: getComputedStyle(document.documentElement).getPropertyValue("--primary-color").trim(),
            borderWidth: 1,
          },
          {
            label: "Actual",
            data: actualData || [],
            backgroundColor: getComputedStyle(document.documentElement)
              .getPropertyValue("--secondary-transparent")
              .trim(),
            borderColor: getComputedStyle(document.documentElement).getPropertyValue("--secondary-color").trim(),
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value) => formatCurrency(value),
            },
          },
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => context.dataset.label + ": " + formatCurrency(context.raw),
            },
          },
        },
      },
    })
  }

  // Expense Pie Chart
  const expenseChartEl = document.getElementById("expensePieChart")
  if (expenseChartEl) {
    const ctx = expenseChartEl.getContext("2d")
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: expenseLabels || [],
        datasets: [
          {
            data: expenseData || [],
            backgroundColor: [
              "#4caf50", // Green
              "#2196f3", // Blue
              "#ff9800", // Orange
              "#9c27b0", // Purple
              "#f44336", // Red
              "#00bcd4", // Cyan
              "#3f51b5", // Indigo
              "#e91e63", // Pink
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const label = context.label || ""
                const value = context.raw || 0
                const total = context.dataset.data.reduce((a, b) => a + b, 0)
                const percentage = Math.round((value / total) * 100)
                return label + ": " + formatCurrency(value) + " (" + percentage + "%)"
              },
            },
          },
        },
      },
    })
  }

  // Monthly Trend Chart
  const trendChartEl = document.getElementById("monthlyTrendChart")
  if (trendChartEl) {
    const ctx = trendChartEl.getContext("2d")
    new Chart(ctx, {
      type: "line",
      data: {
        labels: monthLabels || [],
        datasets: [
          {
            label: "Income",
            data: incomeData || [],
            borderColor: "#4caf50",
            backgroundColor: "rgba(76, 175, 80, 0.1)",
            tension: 0.4,
            fill: true,
          },
          {
            label: "Expenses",
            data: expenseData || [],
            borderColor: "#f44336",
            backgroundColor: "rgba(244, 67, 54, 0.1)",
            tension: 0.4,
            fill: true,
          },
          {
            label: "Savings",
            data: savingsData || [],
            borderColor: "#2196f3",
            backgroundColor: "rgba(33, 150, 243, 0.1)",
            tension: 0.4,
            fill: true,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            ticks: {
              callback: (value) => formatCurrency(value),
            },
          },
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => context.dataset.label + ": " + formatCurrency(context.raw),
            },
          },
        },
      },
    })
  }
}

// Budget progress calculation
function updateBudgetProgress(budgetId, spent, allocated) {
  const progressBar = document.querySelector(`#budget-${budgetId} .progress-bar`)
  const percentageEl = document.querySelector(`#budget-${budgetId} .percentage`)
  const remainingEl = document.querySelector(`#budget-${budgetId} .remaining`)

  if (!progressBar || !percentageEl || !remainingEl) return

  const percentage = (spent / allocated) * 100
  const remaining = allocated - spent

  progressBar.style.width = `${Math.min(percentage, 100)}%`
  percentageEl.textContent = formatPercentage(percentage)
  remainingEl.textContent = formatCurrency(remaining)

  // Update progress bar color based on percentage
  progressBar.classList.remove("progress-bar-danger", "progress-bar-warning", "progress-bar-success")

  if (percentage >= 100) {
    progressBar.classList.add("progress-bar-danger")
  } else if (percentage >= 75) {
    progressBar.classList.add("progress-bar-warning")
  } else {
    progressBar.classList.add("progress-bar-success")
  }
}

// Handle dark/light theme toggle
function toggleTheme() {
  const themeToggle = document.getElementById("theme-toggle-checkbox")
  if (themeToggle) {
    themeToggle.addEventListener("change", function () {
      if (this.checked) {
        document.body.classList.add("dark-theme")
        localStorage.setItem("theme", "dark")
      } else {
        document.body.classList.remove("dark-theme")
        localStorage.setItem("theme", "light")
      }
    })

    // Check for saved theme preference
    const savedTheme = localStorage.getItem("theme")
    if (savedTheme === "dark") {
      themeToggle.checked = true
      document.body.classList.add("dark-theme")
    }
  }
}

// Initialize theme toggle
toggleTheme()