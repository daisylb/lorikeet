import React, { Component } from 'react'
import { render } from 'react-dom'

/**
 * Wraps a React component, passing it a 'cart' prop which contains the current
 * contents of the cart, and updates every time the cart updates.
 * Expects a 'cartClient' prop, which is passed through to the contained
 * component.
 */
export default function cartify(InnerComponent){
  class CartWrapper extends Component {
    constructor(props){
      super(props)
      this.state = {cart: props.cartClient.cart}
    }
    componentDidMount(){
      this.listenerRef = this.props.cartClient.addListener((c) => this.setState({cart: c}))
    }
    componentWillUnmount(){
      this.props.client.removeListener(this.listenerRef)
    }
    render(){
      return <InnerComponent cart={this.state.cart} {...this.props} />
    }
  }
  return CartWrapper
}
