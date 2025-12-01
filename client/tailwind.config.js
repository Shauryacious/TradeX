/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                sans: ['Poppins', 'sans-serif'],
            },
            colors: {
                dark: {
                    bg: '#000000',
                    surface: '#16181C',
                    surfaceHover: '#1D1F23',
                    border: '#2F3336',
                    text: '#E7E9EA',
                    textSecondary: '#71767A',
                },
                primary: {
                    50: '#E8E5FF',
                    100: '#D1CBFF',
                    200: '#A397FF',
                    300: '#7563FF',
                    400: '#472FFF',
                    500: '#1D0BFF',
                    600: '#1709CC',
                    700: '#110799',
                    800: '#0C0566',
                    900: '#060333',
                },
                violet: {
                    50: '#F5F3FF',
                    100: '#EDE9FE',
                    200: '#DDD6FE',
                    300: '#C4B5FD',
                    400: '#A78BFA',
                    500: '#8B5CF6',
                    600: '#7C3AED',
                    700: '#6D28D9',
                    800: '#5B21B6',
                    900: '#4C1D95',
                },
            },
        },
    },
    plugins: [],
}

