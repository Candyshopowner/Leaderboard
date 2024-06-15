const { exec } = require('child_process');

exec('npx chromedriver --version', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error executing command: ${error}`);
    return;
  }
  console.log(`ChromeDriver version: ${stdout}`);
});
