/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/templates/**/*.html',
        './src/static/**/*.js',
    ],
    theme: {
        extend: {
            fontFamily: {
                display: ['"Barlow Condensed"', 'sans-serif'],
                body:    ['"DM Sans"', 'sans-serif'],
                mono:    ['"DM Mono"', 'monospace'],
            },
            colors: {
                ink:   '#1A1A18',
                paper: '#F8F8F7',
                line:  '#E5E3DF',
                mute:  '#6B6860',
                mute2: '#A8A5A0',
                orange: {
                    DEFAULT: '#F25C05',
                    dark:    '#D94F04',
                    wash:    '#FFF0E8',
                },
            },
        }
    },
    plugins: [],
}
