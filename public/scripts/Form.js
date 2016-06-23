import React from 'react'


export var FormInputRow = React.createClass({
    render: function() {
        return (
            <div className="formInputRow">
                <div className="formInputTitle"
                     style={{width: 320, float: 'left', marginTop: 5}}>
                    {this.props.inputName}
                </div>
                <div className="formInputField"
                     style={{marginLeft: 340, marginTop: 5}}>
                    <this.props.inputTag
                                 type={this.props.inputType}
                                 value={this.props.value}
                                 onChange={this.props.handleInputChange.bind(
                                         null, this.props.inputName,
                                         this.props.inputType,
                                         this.props.formName)}
                    />
                </div>
            </div>
        );
    }
});

export var FormSelectInput = React.createClass({
    render: function() {
        var selectOptions = this.props.optionsList.map(function(option) {
            return (
                <option value={option.id} key={option.id}>
                    {option.name}
                </option>
            );
        }.bind(this));
        return (
            <div className="formInputRow">
                <div className="formInputTitle"
                     style={{width: 320, float: 'left', marginTop: 5}}>
                    {this.props.inputName}
                </div>
                <div className="formInputField"
                     style={{marginLeft: 340, marginTop: 5}}>
                    <select
                        value={this.props.value}
                        onLoad={this.props.handleInputChange.bind(
                                null, this.props.inputName,
                                this.props.inputType,
                                this.props.formName)}
                        onChange={this.props.handleInputChange.bind(
                                null, this.props.inputName,
                                this.props.inputType,
                                this.props.formName)}>
                        {selectOptions}
                    </select>
                </div>
            </div>
        );
    }
});

export var FormTitleRow = React.createClass({
    render: function() {
        return (
            <div className="formTitleDiv" style={{marginTop: 30}}>
                <h3>
                    {this.props.formTitle}
                </h3>
            </div>
        );
    }
});
