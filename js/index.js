const csrftoken = decodeURIComponent(/(?:^|;)\s*csrftoken=([^;]+)/.exec(document.cookie)[1])
const localStorageKey = 'au.com.cmv.open-source.lorikeet.cart-data'

function apiFetch(url, params){
  var actualParams = Object.create(params || null)
  actualParams.headers = Object.create(params? params.headers || null : null)
  actualParams.headers['Accept'] = 'application/json'
  actualParams.headers['Content-Type'] = 'application/json'
  actualParams.headers['X-CSRFToken'] = csrftoken
  actualParams.credentials = 'same-origin'
  return fetch(url, actualParams).then((resp) => {
    // Reject the promise if we get a non-2xx return code
    if (resp.ok){
      return resp.json()
    }
    return resp.json().then((x) => Promise.reject(x))
  })
}

class CartEntry {
  constructor(client, data){
    this.client = client
    for (var prop in data){
      if (!data.hasOwnProperty(prop)){
        continue
      }
      if (prop in this){
        console.warn('Skipping prop '+ prop +' because it would override a property')
        continue
      }
      this[prop] = data[prop]
    }
    this.delete = this.delete.bind(this)
  }
  delete(){
    return apiFetch(this.url, {
      method: 'DELETE',
    })
    .then(() => this.client.reloadCart())
  }
}

class CartItem extends CartEntry {
  constructor(client, data){
    super(client, data)
    this.update = this.update.bind(this)
  }
  update(newData){
    return apiFetch(this.url, {
      method: 'PATCH',
      body: JSON.stringify(newData),
    })
    .then(() => this.client.reloadCart())
  }
}

class AddressOrPayment extends CartEntry {
  constructor(client, data){
    super(client, data)
    this.select = this.select.bind(this)
  }
  select(){
    return apiFetch(this.url, {
      method: 'PATCH',
      body: '{"selected": true}',
    })
    .then(() => this.client.reloadCart())
  }
}

export default class CartClient {
  /**
   * @param {string} cartUrl - URL to the shopping cart API endpoint.
   * @param {object=} cartData - Current state of the cart. If provided,
   *     should match the expected strcuture returned by the cart endpoint.
   */
  constructor(cartUrl, cartData){
    // bind all the things
    this.reloadCart = this.reloadCart.bind(this)
    this.addItem = this.addItem.bind(this)
    this.addAddress = this.addAddress.bind(this)
    this.addPaymentMethod = this.addPaymentMethod.bind(this)
    this.checkout = this.checkout.bind(this)

    this.cartUrl = cartUrl
    this.cartListeners = []

    // try to load initial data from localStorage
    var lsString = localStorage.getItem(localStorageKey)
    if (lsString){
      this.processReceivedCart(JSON.parse(lsString), true)
    }

    // If we've been passed in data from the server, try loading it in to see
    // if it's newer. We do this second because we want to trigger a setItem
    // on localStorage if what we've got is newer than what's currently there.
    if (cartData){
      this.processReceivedCart(cartData)
    }

    // do an initial load of the cart, if we didn't already get the data
    // from somewhere
    if (!this.cart) {
      this.reloadCart()
    }

    // add localStorage listener
    window.addEventListener('storage', (ev) => {
      if (ev.key == localStorageKey) {
        this.processReceivedCart(JSON.parse(ev.newValue), true)
      }
    })
  }

  reloadCart(){
    apiFetch(this.cartUrl)
    .then(json => {
      this.processReceivedCart(json)
    })
  }

  processReceivedCart(cart, receivedFromLocalStorage){
    // If the cart we recieved is more stale than what we already have, bail
    if (self.cart && self.cart.updated_at > cart.updated_at) {
      return
    }

    // If we didn't get it _from_ local storage, post it _to_ local storage
    if (!receivedFromLocalStorage){
      localStorage.setItem(localStorageKey, JSON.stringify(cart))
    }

    // Attach the update method to each member of items
    cart.items = cart.items.map(x => new CartItem(this, x))
    cart.delivery_addresses = cart.delivery_addresses.map(x => new AddressOrPayment(this, x))
    cart.payment_methods = cart.payment_methods.map(x => new AddressOrPayment(this, x))

    this.cart = cart
    this.cartListeners.forEach(x => x(this.cart))
  }

  /**
   * Register a listener function to be called every time the cart is updated.
   * @param {function} listener - The listener to add.
   * @return {function} Returns the listener function that was passed in,
   *     so you can pass in an anonymous function and still have something
   *     to pass to removeListener later.
   */
  addListener(listener){
    this.cartListeners.push(listener)
    return listener
  }

  /**
   * @param {function} listener - The listener to remove.
   */
  removeListener(listener){
    this.cartListeners.splice(this.cartListeners.indexOf(listener), 1)
  }

  add(url, type, data){
    return apiFetch(url, {
      method: 'POST',
      body: JSON.stringify({type, data}),
    })
    .then(() => this.reloadCart())
  }

  /**
   * Add an item to the shopping cart.
   * @param {string} type - Type of LineItem to create
   * @param {object} data - Data that the corresponding LineItem serializer
   *     is expecting.
   */
  addItem(type, data){
    return this.add(this.cart.new_item_url, type, data)
  }

  /**
   * Add a delivery address to the shopping cart.
   * @param {string} type - Type of DeliveryAddress to create
   * @param {object} data - Data that the corresponding DeliveryAddress
   * serializer is expecting.
   */
  addAddress(type, data){
    return this.add(this.cart.new_address_url, type, data)
  }

  /**
   * Add a delivery address to the shopping cart.
   * @param {string} type - Type of PaymentMethod to create
   * @param {object} data - Data that the corresponding PaymentMethod
   * serializer is expecting.
   */
  addPaymentMethod(type, data){
    return this.add(this.cart.new_payment_method_url, type, data)
  }

  checkout(){
    return apiFetch(this.cart.checkout_url, {method: 'POST'})
  }
}
