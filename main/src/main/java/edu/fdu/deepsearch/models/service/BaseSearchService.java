package edu.fdu.deepsearch.models.service;

import edu.fdu.deepsearch.models.queryentity.CommonQuery;
import edu.fdu.deepsearch.models.service.searchrule.SearchServiceRule;

import java.io.Serializable;

/**基础搜索服务
 *继承抽象Query服务类，CommonQuery，以及SearchServiceRule，以实现search
 */
public abstract class BaseSearchService<A extends AbstractQueryService, Q extends CommonQuery, SR extends SearchServiceRule, R2>
        implements Serializable {
}
