import React, { Component } from 'react'
import { render } from 'react-dom'

/**
 * Wraps a React component, passing it a 'cart' prop which contains the current
 * contents of the cart, and updates every time the cart updates.
 * Expects a 'cartClient' prop, which is passed through to the contained
 * component.
 */
export default function cartify(InnerComponent){
  var wrapper = class extends Component {
    constructor(props, context){
      super(props, context)
      this.state = {cart: context.cartClient.cart}
    }
    componentDidMount(){
      this.listenerRef = this.context.cartClient.addListener((c) => this.setState({cart: c}))
    }
    componentWillUnmount(){
      this.context.cartClient.removeListener(this.listenerRef)
    }
    render(){
      return <InnerComponent cartClient={this.context.cartClient} cart={this.state.cart} {...this.props} />
    }
  }
  var innerName = InnerComponent.displayName || InnerComponent.name || 'Inner'
  wrapper.displayName = `CartWrapper(${innerName})`
  wrapper.contextTypes = CartProvider.childContextTypes
  return wrapper
}

export class CartProvider extends Component {
  getChildContext(){
    return {cartClient: this.props.client}
  }
  render(){
    return <span>{this.props.children}</span>
  }
}
CartProvider.childContextTypes = {
    cartClient: React.PropTypes.object,
}