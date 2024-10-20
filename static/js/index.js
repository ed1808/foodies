const PRODUCTS_API_URL = '/products/api/';
const CUSTOMERS_API_URL = '/customers/api/';
const ORDERS_API_URL = '/orders/api/add-order/';

let totalItems = 1;

const addRow = (productsArray, tableBody) => {
	const newRow = createRow(productsArray);
	tableBody.append(newRow);
}

const createRow = (productsArray) => {
	const productSelect = document.createElement('select');
	productSelect.name = `product_${totalItems}`;
	productSelect.id = `product_${totalItems}`;
	productSelect.className = 'p-3 block text-sm text-gray-900 bg-gray-50 rounded border border-gray-300 focus:ring-orange-500 focus:border-orange-500';
	productSelect.setAttribute('onchange', `getProductPrice(this)`);
	productSelect.setAttribute('required', 'true');

	const quantityInput = document.createElement('input');
	quantityInput.type = 'number';
	quantityInput.name = `quantity_${totalItems}`;
	quantityInput.id = `quantity_${totalItems}`;
	quantityInput.value = '0';
	quantityInput.min = '1';
	quantityInput.className = 'p-3 block text-sm text-gray-900 bg-gray-50 rounded border border-gray-300 focus:ring-orange-500 focus:border-orange-500';
	quantityInput.setAttribute('onchange', `calculateTotalValue(this)`);
	quantityInput.setAttribute('onblur', `calculateTotalValue(this)`);

	const productPriceSpan = document.createElement('span');
	productPriceSpan.id = `product-price-${totalItems}`;
	productPriceSpan.textContent = '-';

	const dollarSign = document.createElement('span');
	dollarSign.textContent = '$';

	const deleteButton = document.createElement('button');
	deleteButton.type = 'button';
	deleteButton.className = 'flex items-center border-2 border-red-500 text-red-500 hover:bg-red-500 focus:ring-4 focus:outline-none focus:ring-red-500 font-medium rounded text-sm hover:text-white p-3 text-center transition-colors ease-linear';
	deleteButton.title = 'Eliminar';
	deleteButton.setAttribute('onclick', `deleteRow('row-${totalItems}')`);
	deleteButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" color="currentColor" fill="none">
									<path d="M19.5 5.5L18.8803 15.5251C18.7219 18.0864 18.6428 19.3671 18.0008 20.2879C17.6833 20.7431 17.2747 21.1273 16.8007 21.416C15.8421 22 14.559 22 11.9927 22C9.42312 22 8.1383 22 7.17905 21.4149C6.7048 21.1257 6.296 20.7408 5.97868 20.2848C5.33688 19.3626 5.25945 18.0801 5.10461 15.5152L4.5 5.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
									<path d="M3 5.5H21M16.0557 5.5L15.3731 4.09173C14.9196 3.15626 14.6928 2.68852 14.3017 2.39681C14.215 2.3321 14.1231 2.27454 14.027 2.2247C13.5939 2 13.0741 2 12.0345 2C10.9688 2 10.436 2 9.99568 2.23412C9.8981 2.28601 9.80498 2.3459 9.71729 2.41317C9.32164 2.7167 9.10063 3.20155 8.65861 4.17126L8.05292 5.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
									<path d="M9.5 16.5L9.5 10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
									<path d="M14.5 16.5L14.5 10.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
								</svg>`;

	const emptyOption = document.createElement('option');
	emptyOption.textContent = 'Seleccionar';
	emptyOption.value = '';

	productSelect.appendChild(emptyOption);

	for (let i = 0; i < productsArray.length; i++) {
		const option = document.createElement('option');
		option.value = productsArray[i].id;
		option.textContent = productsArray[i].name;
		productSelect.appendChild(option);
	}

	const row = document.createElement('tr');
	row.id = `row-${totalItems}`;

	const productCell = document.createElement('td');
	productCell.className = 'py-3 border-b border-b-gray-200';
	productCell.append(productSelect);

	const quantityCell = document.createElement('td');
	quantityCell.className = 'py-3 border-b border-b-gray-200';
	quantityCell.append(quantityInput);

	const priceCell = document.createElement('td');
	priceCell.className = 'w-10 py-3 border-b border-b-gray-200';
	priceCell.append(dollarSign, productPriceSpan);

	const deleteCell = document.createElement('td');
	deleteCell.className = 'flex items-center justify-center py-3 border-b border-b-gray-200';
	deleteCell.append(deleteButton);

	row.append(productCell, quantityCell, priceCell, deleteCell);

	return row;
}

const calculateTotalValue = (elem) => {
	const splittedId = elem.id.split('_');
	const id = splittedId[1];
	const productPrice = document.querySelector(`#product-price-${id}`);

    const basePrice = elem.getAttribute('base-price');
    const newPrice = Number(basePrice * elem.value);

    productPrice.textContent = newPrice;
};

const deleteRow = (rowId) => {
	const row = document.querySelector(`#${rowId}`);
	row.remove();
	totalItems -= 1;
}

const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const getCustomers = async () => {
	try {
		const response = await fetch(CUSTOMERS_API_URL);

		if (!response.ok) {
			throw new Error(response.statusText);
		}

		return await response.json();

	} catch (error) {
		throw new Error(error);
	}
}

const getProductPrice = (elem) => {
	const value = elem.value;
	const splittedId = elem.id.split('_');
	const id = splittedId[1];
	const productPrice = document.querySelector(`#product-price-${id}`);
    const quantityElem = document.querySelector(`#quantity_${id}`);

	fetch(`${PRODUCTS_API_URL}${value}/`)
		.then((response) => response.json())
		.then((data) => {
			productPrice.textContent = Number(data['price']);
            quantityElem.value = 1;
            quantityElem.setAttribute('base-price', data['price']);
		})
		.catch((error) => console.error(error));
};

const getProducts = async () => {
	try {
		const response = await fetch(PRODUCTS_API_URL);

		if (!response.ok) {
			throw new Error(response.statusText);
		}

		return await response.json();

	} catch (error) {
		throw new Error(error);
	}
}

document.addEventListener('DOMContentLoaded', async () => {
	const url = new URL(window.location.href);
	const pathname = url.pathname;

	if (pathname.endsWith('add-order/')) {

		const customerSelect = document.querySelector('#customer');
		const form = document.querySelector('#create-order-form');

		const customers = await getCustomers();
		const products = await getProducts();

		const loadingIndicator = document.querySelector('#loading-indicator');

		for (let i = 0; i < customers.length; i++) {
			const option = document.createElement('option');
			option.value = customers[i].id;
			option.textContent = customers[i].name;
			customerSelect.appendChild(option);
		}

		const formContainer = document.querySelector('#form-container tbody');
		const addRowButton = document.querySelector('#add-row');

		addRow(products, formContainer);

		addRowButton.addEventListener('click', () => {
			totalItems += 1;

			addRow(products, formContainer);
		});

		form.addEventListener('submit', (event) => {
			event.preventDefault();

			loadingIndicator.classList.replace('hidden', 'grid');

			let requestData = {};
			requestData.items = [];

			let productsArray = [];
			let quantityArray = [];
			let itemsArray = [];

			const formData = new FormData(form);

			for (const key of formData.keys()) {
				if (key.includes('product')) {
					productsArray.push([key, formData.get(key)]);
				} else if (key.includes('quantity')) {
					quantityArray.push([key, formData.get(key)]);
				}
			}

			for (let i = 0; i < productsArray.length; i++) {
				const product = productsArray[i];
				const quantity = quantityArray[i];

				itemsArray.push({
					product: product[1],
					quantity: quantity[1],
				});
			}

			requestData['customer'] = formData.get('customer');
			requestData.items = itemsArray;

			const requestOptions = {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': getCookie('csrftoken'),
				},
				mode: 'same-origin',
				body: JSON.stringify(requestData),
			}

			fetch(ORDERS_API_URL, requestOptions)
				.then(response => response.json())
				.then(data => {
					if (data.status === 'success') {
						window.location.href = '/orders/';
					} else {
						alert(data.message);
					}
					
					loadingIndicator.classList.replace('grid', 'hidden');
				})
				.catch((error) => console.error(error));
		});
	}
});
