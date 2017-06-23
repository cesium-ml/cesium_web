import React, { Component } from 'react';
import { connect } from 'react-redux';
import { showNotification } from 'baselayer/components/Notifications';
import "../../../node_modules/bokehjs/build/js/bokeh.js";
import "../../../node_modules/bokehjs/build/css/bokeh.css";
import Select from 'react-select';
import 'react-select/dist/react-select.css';
import * as Action from '../actions';
import { reduxForm } from 'redux-form';
import { Form, SubmitButton} from './Form';

function bokeh_render_plot(node, docs_json, render_items) {
  // Create bokeh div element
  var bokeh_div = document.createElement("div");
  var inner_div = document.createElement("div");
  bokeh_div.setAttribute("class", "bk-root" );
  inner_div.setAttribute("class", "bk-plotdiv");
  inner_div.setAttribute("id", render_items[0].elementid);
  bokeh_div.appendChild(inner_div);
  node.appendChild(bokeh_div);

  // Generate plot
  Bokeh.safely(function() {
    Bokeh.embed.embed_items(docs_json, render_items);
  });

  // Set zIndex of bokeh html canvas
  var style=document.createElement('style');
  style.type='text/css';
  if(style.styleSheet){
      style.styleSheet.cssText='div.bk-canvas-wrapper{z-index: 0!important;}';
  }else{
      style.appendChild(document.createTextNode('div.bk-canvas-wrapper{z-index: 0!important;}'));
  }
  document.getElementsByTagName('head')[0].appendChild(style);
}


let PlotForm = (props) => {
  const { fields: { tags },
          error, resetForm, submitting, handleSubmit, featuresOptions, generatePlot, featuresetId} = props;
  console.log("In PlotForm");
  console.log(tags);

  let options = featuresOptions;

  // Limit number of selections to 4
  if ((typeof tags.value === 'string' || tags.value instanceof String) ) {
    let selected = tags.value.split(',');
    if (selected.length >= 4) {
      options = featuresOptions.filter(option => (selected.indexOf(option.value) > -1));
    }
  }

  return (
      <form className="form-inline" onSubmit={handleSubmit(generatePlot)} error={error}>
        <div className="form-group" style={{width:'70%'}}>
          <Select
            multi
            joinValues
            simpleValue
            value={tags.value}
            onChange={tags.onChange}
            placeholder="Select up to four features for a scatter plot"
            options={options}
            style={{zIndex: 10}}
            {...tags}
            onBlur={() => tags.onBlur(tags.value)}
          />
        </div>
        <div className="form-group" style={{width:'30%'}}>
          <button
            type="submit"
            className="btn btn-primary"
            submiting={submitting}
          >
          Plot Selected Features
          </button>
        </div>
      </form>
  );
};

PlotForm = reduxForm({
  form: 'features2plot',
  fields: ['tags', 'featuresetId'],
}, null)(PlotForm);

// TODO Make variable featuresetId
const pfMapStateToProps = (state, ownProps) => {
  console.log("In map state to props")
  console.log(state);

  var featureset = state.featuresets.filter(fs => (fs.id === ownProps.initialValues.featuresetId))[0];
  var featuresOptions = featureset.features_list.map((feature_name, idx) => {return {value:feature_name, label:feature_name}; });

  var plot = state.plots.filter(plot => (plot.featuresetId === ownProps.initialValues.featuresetId))[0];
  var tags = [];
  if (plot != null) {
    tags = plot.tags
  }

  return {
    tags: tags,
    featuresOptions: featuresOptions
  }
};

const pfMapDispatchToProps = dispatch => (
  {
    generatePlot: form => dispatch(Action.generatePlot(form))
  }
);

PlotForm = connect(pfMapStateToProps, pfMapDispatchToProps)(PlotForm);


class Plot extends Component {
  constructor(props) {
    super(props);
  }

  componentDidUpdate() {
    const { plot } = this.props;
    var docs_json = JSON.parse(plot.docs_json);
    var render_items = JSON.parse(plot.render_items);
    var node = document.getElementById('plot' + this.props.featuresetId.toString());
    if (node && docs_json && render_items) {
      node.innerHTML = "";
      bokeh_render_plot(node, docs_json, render_items);
    }
  }

  render() {
    return (<div id={`plot${this.props.featuresetId}`}/>);
  }
}
// TODO add Plot.propTypes

const plotMapStateToProps = (state, ownProps) => {
  console.log("In plotMapStateToProps");
  var plot = state.plots.filter(plot => (plot.featuresetId === ownProps.featuresetId))[0];
  return {
    plot: plot
  };
};

Plot = connect(plotMapStateToProps, null)(Plot);

export {Plot, PlotForm};
