import asyncio
import os
from playwright.async_api import async_playwright
import json


with open('data/input/custom_headers.json','r') as f:
   custom_headers = json.load(f)


with open('data/input/queries/query_300.json', 'r') as f:
    queries_dataset = json.load(f)


with open('data/input/proxy_config.json','r') as f:
    proxy_configs = json.load(f)




async def save_html(page, departure, destination, departure_date, return_date, country_id):
    filename = f"html_pages/{country_id}_{departure}_to_{destination}_on_{departure_date}_back_{return_date}.html"
    if not os.path.exists('html_pages'):
        os.makedirs('html_pages')
    try:
        body = await page.content()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(body)
        print(f"Saved HTML to {filename}")
    except Exception as e:
        print(f"Error saving HTML: {e}")

async def handle_response(response, departure, destination, departure_date, return_date,country_id):
    if response.url.startswith("https://www.google.com/_/TravelFrontendUi/data/travel.frontend.flights.FlightsFrontendService/GetShopping") and response.request.resource_type == 'xhr':
        if not os.path.exists('responses'):
            os.makedirs('responses')
        filename = f'responses/{country_id}_{departure}_to_{destination}_on_{departure_date}_back_{return_date}.json'
        try:
            body = await response.text()
            with open(filename, 'w') as f:
                f.write(body)
            print(f"Saved response to {filename}")
        except Exception as e:
            print(f"Error processing response: {e}")


async def run_query_with_multiple_proxies(departure, destination, departure_date, return_date, proxy_configs, timeout):
    tasks = []
    # Dictionary to map tasks to their corresponding browsers to close them on timeout
    task_to_browser = {}

    for proxy_config in proxy_configs:
        browser = await launch_browser(proxy_config)  # Assumed function to launch browser
        task = asyncio.create_task(main(departure, destination, departure_date, return_date, proxy_config, browser))
        tasks.append(task)
        task_to_browser[task] = browser

    done, pending = await asyncio.wait(tasks, timeout=timeout, return_when=asyncio.ALL_COMPLETED)

    # Attempt to close any pending tasks' browsers due to timeout
    for task in pending:
        print(f"Task {task} timed out. Closing browser.")
        browser = task_to_browser[task]
        await browser.close()  # Ensure this is a safe call if browser is already closed
        task.cancel()

    # Handle done tasks normally
    for task in done:
        try:
            await task  # This will re-raise any exceptions caught within the task
        except Exception as e:
            print(f"Task completed with exception: {e}")



async def run_queries_sequentially_with_multiple_proxies(timeout=80):  # Adjusted timeout as needed
    for entry in queries_dataset:
        await run_query_with_multiple_proxies(entry['departure'], entry['destination'], entry['departure_date'], entry['return_date'], proxy_configs, timeout)

async def is_browser_alive(browser):
    try:
        # Attempt to create a new page to check if the browser is responsive
        page = await browser.new_page()
        await page.close()
        return True
    except Exception as e:
        print(f"Browser check failed: {e}")
        return False


async def launch_browser(proxy_config):
    async with async_playwright() as p:
        browser = await p.chromium.launch(proxy={
            "server": proxy_config["server"],
            "username": proxy_config["username"],
            "password": proxy_config["password"]
        }, headless=True)
    return browser






async def main(departure, destination, departure_date, return_date, proxy_config, browser):
    country_id = proxy_config["country"]
    headers = custom_headers.get(country_id, {"Accept-Language": "en-US,en;q=0.9", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"})


    async with async_playwright() as p:
        print('Launching Browser...')

        browser = await p.chromium.launch(proxy={
            "server": proxy_config["server"],
            "username": proxy_config["username"],
            "password": proxy_config["password"]
        }, headless=True)


        print("Creating incognito browser context with custom user agent")
        headers = custom_headers.get(country_id, {
        "User-Agent": "Default-User-Agent",
        "Accept-Language": "en-US,en;q=0.9"
    })

        # Create the context with the specific headers for the country
        context = await browser.new_context(
            user_agent=headers["User-Agent"],  # This sets the user agent
            extra_http_headers={k: v for k, v in headers.items() if k != "User-Agent"}  # This sets all other headers except the user agent
    )

        # Open a new page within the configured context
        print("Opening a new page")
        page = await context.new_page()

        page.on('response', lambda response: asyncio.create_task(handle_response(response, departure, destination, departure_date, return_date, country_id)))


        initial_url = "https://www.google.com/travel/flights"
        await page.goto(initial_url, wait_until="networkidle")
        await page.wait_for_timeout(10)  # Wait for potential redirects

        # Corrected logic for handling redirects; adjust as necessary.
        current_url = page.url
        if current_url != initial_url:
            print("Handling redirection with keyboard inputs...")
            for _ in range(3):  # Example logic; adjust based on actual page behavior.
                await page.keyboard.press('Tab')
                await asyncio.sleep(1)  # Adjust timing as necessary.
            await page.keyboard.press('Enter')
        else:
            print("No redirection, proceeding with the original workflow")
        
        await asyncio.sleep(5)
        await save_html(page, departure, destination, departure_date, return_date,country_id)
        print("Waiting")
        await asyncio.sleep(2)
        await page.click('input[type="text"][role="combobox"]')
        print("clicked")
        await page.keyboard.down('Meta')
        await page.keyboard.press('A')
        await page.keyboard.up('Meta')
        await page.keyboard.press('Backspace')
        await page.keyboard.type(departure)
        await asyncio.sleep(2)
        await page.keyboard.press('Tab')
        await asyncio.sleep(2)
        await page.keyboard.press('Tab')
        await asyncio.sleep(1)
        # Simulate typing 'New York' into the destination field and pressing Enter
        await page.keyboard.type(destination)
        await asyncio.sleep(2)
        await page.keyboard.press('Tab')
        await page.keyboard.press('Tab')
        await asyncio.sleep(1)
        # Simulate typing the departure date and pressing Tab
        await page.keyboard.type(departure_date)
        await asyncio.sleep(1)
        await page.keyboard.press('Tab')

        await asyncio.sleep(2)
        # Simulate typing the return date and pressing Enter
        await page.keyboard.type(return_date)
        await asyncio.sleep(2)
        await page.keyboard.press('Enter')
        await page.keyboard.press('Enter')

        # Wait for a moment to see the result
        await asyncio.sleep(1)
        await page.keyboard.press('Enter')
        await asyncio.sleep(10)

        # Correctly closing context and browser at the end of the function.
        await context.close()
        await browser.close()


asyncio.run(run_queries_sequentially_with_multiple_proxies(timeout=80))  # Set your desired timeout in seconds