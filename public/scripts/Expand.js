import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import {toggleExpander} from './actions'
import Dot from './Dot'


export class Expand extends Component {
  render() {
    let style = {
      a: {textDecoration: 'none'},
      sign: {
        fontSize: '200%',
        fontWeight: 'bold'
      },
      children: {
        position: 'relative',
        width: '100%',
        zIndex: 1000,
        background: 'white',
        border: '1px solid LightGray',
        paddingLeft: '2em',
        marginTop: '0.5em',
        marginBottom: '1em',
        ...(this.props.expandBoxStyle)
      },
      ...(this.props.style)
    }

    let add = (
      <span>
        <span style={style.sign}><Dot height='0.7em'
              value='+' style={style.dot}/> </span>
        {this.props.label}
      </span>);

    let shrink = (
      <span>
        <span style={style.sign}><Dot height='0.7em'
              value='-' style={style.dot}/> </span>
        {this.props.label}
      </span>);

    return (
      <div style={{...style, ...(this.props.style)}}>

        <a style={style.a} onClick={this.props.toggle}>
          { this.props.opened ? shrink : add }
        </a>

        {(this.props.opened) &&

          <div style={style.children}>
            {this.props.opened ? this.props.children : null}
          </div>
        }

      </div>
    )
  }
}

let mapStateToProps = (state, ownProps) => {
  return {
    opened: state.expander.opened[ownProps.id]
  }
}

let mapDispatchToProps = (dispatch, ownProps) => {
  return {
    toggle: () => {dispatch(toggleExpander(ownProps.id))}
  }
}

Expand = connect(mapStateToProps, mapDispatchToProps)(Expand)

export {Expand as default}
