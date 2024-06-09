const fs = require('fs');
const parse = require('csv-parser');
const readline = require('readline');

// Function to read the CSV file and parse its content
function readCSV(filePath) {
    return new Promise((resolve, reject) => {
        const questions = [];
        fs.createReadStream(filePath)
            .pipe(parse({ delimiter: ',' }))
            .on('data', (row) => {
                questions.push(row);
            })
            .on('end', () => {
                resolve(questions);
            })
            .on('error', (error) => {
                reject(error);
            });
    });
}

// Function to display a question and prompt user for answer
function displayQuestion(question) {
    console.log('\nPregunta:\n', question.Pregunta, '\n');
    console.log('1:', question['Opción 1']);
    console.log('2:', question['Opción 2']);
    console.log('3:', question['Opción 3']);
    console.log('4:', question['Opción 4']);
}

// Function to check if the answer is correct
function checkAnswer(userAnswer, correctAnswer) {
    return userAnswer === correctAnswer;
}

// Function to ask a single question
function askQuestion(rl, question) {
    return new Promise((resolve, reject) => {
        displayQuestion(question);
        rl.question('\nIntroduzca respuesta (1, 2, 3, or 4): ', (answer) => {
            resolve(answer);
        });
    });
}

// Main function to run the program
async function main() {
    const filePath = 'enter/your/path/to/file.csv'; // Path to your CSV file
    const questions = await readCSV(filePath);
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    for (let i = 0; i < questions.length; i++) {
        const question = questions[i];
        const userAnswer = await askQuestion(rl, question);
        const isCorrect = checkAnswer(userAnswer, question['Opción correcta']);
        if (isCorrect) {
            console.log('\n¡Respuesta correcta!');
        } else {
            console.log('\nIncorrecto. La respuesta correcta es:', question['Opción correcta']);
        }
    }
    
    console.log('\nTodas las preguntas se han contestado. Se finaliza el programa.');
    rl.close();
}

main();
