import React from 'react';
import { connect } from 'react-redux';

let UserProfile = props => (
  <div style={props.style}>{props.profile.username}</div>
);
UserProfile.propTypes = {
  style: React.PropTypes.object.isRequired,
  profile: React.PropTypes.object.isRequired
};

const mapStateToProps = state => (
  {
    profile: state.profile
  }
);

UserProfile = connect(mapStateToProps)(UserProfile);

export default UserProfile;
