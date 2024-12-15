const puppeteer = require('puppeteer');
const args = process.argv;
const [url, test_id, test_type, applicant] = args.slice(2);

const generate_pdf = async () => {
    /*
        Function Description:
        - Launch a Browser instance and add a new page in it
        - Currently headless is false, thus all operations will be visible to user
        - Afterawards, pdf is generated on said url
    */
    const browser = await puppeteer.launch({headless: true});
    const page = await browser.newPage();

    await page.goto(url, {waitUntil: 'networkidle0'});
    await page.setViewport({
        width: 1080,
        height: 720,
    });
    const pdf = await page.pdf({ format: 'A4' });
    console.log(pdf)
}

generate_pdf();