/* Usage:
 *
 * <FoldableRow>
 *   <tr>Table row goes here</tr>
 *   <... whatever to expand when clicking row goes here ...>
 * </FoldableRow>
 *
 * The second element can be, e.g., another row in the table.
 * */

import React, { Component } from 'react'
import {colorScheme as cs} from './colorscheme'

export class FoldableRow extends Component {
  constructor(props) {
    super(props)
    this.state = {folded: true}
    this.toggleFold = this.toggleFold.bind(this)
  }

  toggleFold() {
    this.setState({folded: !this.state.folded})
  }

  render() {
    let children = React.Children.toArray(this.props.children)

    let openStyleHeader = {
      //fontWeight: 'bold'
      background: cs.blue,
      color: 'white'
    }

    let openStyleContent = {
      background: cs.lightGray,
      fontSize: '80%'
    }

    let row = children[0]
    row = React.cloneElement(row, {
      onClick: () => this.toggleFold(),
      style: this.state.folded ? {} : openStyleHeader
    })

    let expanded = children.slice(1)
    expanded = expanded.map((e, idx) => (
      React.cloneElement(
        e, {
          style: this.state.folded ? {} : openStyleContent,
          key: idx
        })
    ))

    return (
      <tbody>
        {row}
        {(!this.state.folded) && expanded}
      </tbody>
    )
  }
}

export { FoldableRow as default }
