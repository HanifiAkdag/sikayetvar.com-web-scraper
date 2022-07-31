# sikayetvar.com web scraper
[sikayetvar.com](https://sikayetvar.com) is an online complaint platform where customers publicly share their complaints about products or companies to help other possible customers.

scraper.py is a simple web scraper that scrapes complaints from [sikayetvar.com](https://sikayetvar.com) and saves it to a CSV file.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Running the following bash command will scrape the complaints of the brand from starting page to ending page (both inclusive). If a file already exists for the same brand, program will ask whether you want to overwrite, append or create a new file.

```bash
python scraper.py <brand> <start page> <end page>
```