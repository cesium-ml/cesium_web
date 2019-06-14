import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';

let UserProfile = props => (
  <div style={props.style}>{props.profile.username}</div>
);
UserProfile.propTypes = {
  style: PropTypes.object.isRequired,
  profile: PropTypes.object.isRequired
};

const mapStateToProps = state => (
  {
    profile: state.profile
  }
);

UserProfile = connect(mapStateToProps)(UserProfile);

export default UserProfile;
