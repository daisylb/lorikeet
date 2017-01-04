const csrftoken = decodeURIComponent(/(?:^|;)\s*csrftoken=([^;]+)/.exec(document.cookie)[1])

function makeUpdate(client){
  /**
   * Update method for LineItems.
   */
  return function(newData){
    // Note: We have to reload the entire cart rather than just copying the
    // data we got back into the server, because adding/modifying the cart could
    // change other things e.g. multiple-line-item discounts
    return fetch(this.url, {
      method: 'PATCH',
      credentials: 'same-origin',
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(newData),
    })
    .then(response => response.json())
    .then(() => client.reloadCart())
  }
}

function makeDelete(client){
  /**
   * Delete method for LineItems.
   */
  return function(newData){
    return fetch(this.url, {
      method: 'DELETE',
      credentials: 'same-origin',
    })
    .then(() => client.reloadCart())
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
    this.reloadCart.bind(this)
    this.addItem.bind(this)

    this.cartUrl = cartUrl
    if (cartData){
      this.postProcessCart(cartData)
    }
    this.cartListeners = []

    // do an initial load of the cart, if we didn't already get the data
    // from the server
    if (!cartData) {
      this.reloadCart()
    }
  }

  reloadCart(){
    fetch(this.cartUrl, {credentials: 'same-origin'})
    .then(response => response.json())
    .then(json => {
      this.postProcessCart(json)
      this.cartListeners.forEach(x => x(this.cart))
    })
  }

  postProcessCart(cart){
    // Attach the update method to each member of items
    cart.items.forEach(x => {
      x.update = makeUpdate(this).bind(x)
      x.delete = makeDelete(this).bind(x)
    })
    this.cart = cart
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

  /**
   * Add an item to the shopping cart.
   * @param {string} type - Type of LineItem to create
   * @param {object} data - Data that the corresponding LineItem serializer
   *     is expecting.
   */
  addItem(type, data){
    return fetch(this.cartUrl + 'new/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({type, data}),
    })
    .then(response => response.json())
    .then(() => this.reloadCart())
  }
}