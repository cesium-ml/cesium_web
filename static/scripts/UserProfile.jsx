import React from 'react';
import { connect } from 'react-redux';

let UserProfile = (props) => {
  return (
    <div style={props.style}>{props.profile.username}</div>
  );
};

const mapStateToProps = state => (
  {
    profile: state.profile
  }
);

UserProfile = connect(mapStateToProps)(UserProfile);

export default UserProfile;
