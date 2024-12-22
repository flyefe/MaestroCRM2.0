/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    // "./templates/**/*.html",        // All HTML files in templates directory
    // "./**/*.html",                  // Catch any stray HTML files in the project
    // "./static/**/*.js",             // Include JS files inside static (if applicable)
    // "./crm/**/*.html",              // If templates are inside app directories

    './crm/**/templates/**/*.html',
    './templates/**/*.html', // Adjust this path to match where your Django templates are stored.
    './static/**/*.js',      // Include your static JS files if you're using Tailwind classes in JavaScript.
    './static/**/*.css',     // Optional: Include static CSS if Tailwind classes are dynamically generated there.
    "./crm/**/*.html",              // If templates are inside app directories
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
};
