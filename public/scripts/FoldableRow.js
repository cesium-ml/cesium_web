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

    let row = children[0]
    row = React.cloneElement(row, {onClick: () => this.toggleFold()})

    let expanded = children.slice(1)

    return (
      <tbody>
        {row}
        {(!this.state.folded) && expanded}
      </tbody>
    )
  }
}

export { FoldableRow as default }
