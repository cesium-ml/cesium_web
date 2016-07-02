import React, { Component, PropTypes } from 'react'

export class AddExpand extends Component {
  constructor(props) {
    super(props);
    this.state = {folded: true};
    this.toggle = this.toggle.bind(this);
  }

  toggle() {
    this.setState({folded: !this.state.folded});
  }

  render() {
    let style = {
      a: {textDecoration: 'none'},
      sign: {
        fontSize: '200%',
        fontWeight: 'bold'
      }
    }

    let add = (
      <span>
        <span style={style.sign}>+ </span>
        {this.props.label}
      </span>);

    let shrink = (
      <span>
        <span style={style.sign}>- </span>
        {this.props.label}
      </span>);

    return (
      <div>

        <a style={style.a} onClick={this.toggle}>
          { this.state.folded ? add : shrink }
        </a>

        <div style={{marginLeft: '2em'}}>
          { this.state.folded ? null : this.props.children }
        </div>

      </div>
    )
  }
}
