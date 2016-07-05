import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import {toggleExpander} from './actions'


export class AddExpand extends Component {
  render() {
    let style = {
      a: {textDecoration: 'none'},
      display: this.props.opened ? 'inline' : 'inline-block',
      paddingRight: '1em',
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

AddExpand = connect(mapStateToProps, mapDispatchToProps)(AddExpand)
