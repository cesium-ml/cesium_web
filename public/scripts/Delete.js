import React from 'react'

var Delete = (props) => {
  let style = {
    display: 'inline-block'
  }
  return (
    <a style={style} onClick={(e) => {
      e.stopPropagation();
      props.delete(props.ID)
    }}>Delete {props.typeName}</a>
  )
}

export default Delete;
