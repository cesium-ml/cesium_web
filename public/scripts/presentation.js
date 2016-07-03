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
      },
      children: {
        border: '1px solid lightgray',
        paddingLeft: '2em',
        marginTop: '0.5em',
        marginBottom: '1em'
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
      <div style={style}>

        <a style={style.a} onClick={this.toggle}>
          { this.state.folded ? add : shrink }
        </a>

        <div style={{marginLeft: '2em'}}>
          { this.state.folded ? null : <div style={style.children}>{this.props.children}</div> }
        </div>

      </div>
    )
  }
}
